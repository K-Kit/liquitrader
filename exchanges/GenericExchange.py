import asyncio
import typing
import itertools
import time
import os
import sys

import ccxt
import ccxt.async_support as ccxt_async

from utils.CandleTools import candles_to_df, candle_tic_to_df, get_change_between_candles
from utils.AverageCalcs import calc_average_price_from_hist, calculate_from_existing

# TODO async update balances every min


# DEFAULT_WALLET_VALUES = [('free',0),( 'used',0),('total',0),('current_value',0),( 'trades',None),( 'last_id',0), ('current_average', None) ]

class GenericExchange:
    """
    Interface
        get_candlesticks()

        get_pairs()

        place_buy_order()

        place_sell_order()


    Needs
        Which candlesticks to get
        Which pairs to get
        Which exchange to use


    Returns
        Candlestick data
        Pair data
    """

    # ----
    def __init__(self,
                 exchange_id: str,
                 quote_currency: str,
                 starting_balance: float,
                 access_keys: typing.Dict[typing.Union[str, str], typing.Union[str, str]],
                 candle_timeframes: typing.List[str]):

        self.pairs = {}
        # moved candles to a seperate dict to make working with pairs easier / cheaper
        self.candles = {}
        # this is the amount of quote currency we hold
        self.balance = None

        # create default dict to store balances, averages, trade history, last_order_id
        # makes sense to calculate averages in the exchange since we'll need to be able to
        # fetch trade history during average calculation, couldnt think of a clean way to do this from a separate class
        # self.wallet = {}

        self._access_keys = access_keys

        self.quote_currency = quote_currency.upper()  # second part of currency pair
        self._candle_timeframes = candle_timeframes

        # initialize standard and sync client
        self._exchange_class = getattr(ccxt, exchange_id)
        self._exchange_class_async = getattr(ccxt_async, exchange_id)

        self._client = None
        self._client_async = None

        self.balance = starting_balance
        self.quote_price = 0
        self.quote_change = 0

        self._loop = asyncio.get_event_loop()

        self._ticker_upkeep_call_schedule = 1  # Call ticker_upkeep() every 1s
        self._candle_upkeep_call_schedule = 60  # Call candle_upkeep() every 60s
        self._quote_change_upkeep_call_schedule = 60  # Call quote_change_upkeep() every 60s
        self._balance_upkeep_call_schedule = 65

        self.quote_change_info = {'1h': 0, '4h': 0, '24h': 0, '6h': 0, '12h': 0}

        # Connect to exchange
        self._init_client_connection()

    # ----
    def _init_client_connection(self):
        # initialize synchronous client

        options = {
            'adjustForTimeDifference': True,  # ←---- resolves the timestamp
        }

        self._client = self._exchange_class({
            'options': options,
            'apiKey': self._access_keys['public'],
            'secret': self._access_keys['secret'],
            'timeout': 20000,
            'enableRateLimit': True,
            'parseOrderToPrecision': True
        })

        async_params = {
            'options': options,
            'apiKey': self._access_keys['public'],
            'secret': self._access_keys['secret'],
            'timeout': 20000,
            'enableRateLimit': False,
            'asyncio_loop': self._loop
        }

        if hasattr(sys, 'frozen'):
            async_params['cafile'] = os.path.join(os.path.dirname(sys.executable), 'lib', 'cacert.pem')

        # initialize async client
        self._client_async = self._exchange_class_async(async_params)

    # ----
    async def initialize(self):
        # Mandatory to call this before any other calls are made to Bittrex
        await self._client_async.load_markets()
        self._initialize_pairs()
        await self.load_all_candle_histories(num_candles=500)

    # ----
    def start(self):
        self._loop.create_task(self._candle_upkeep())
        self._loop.create_task(self._ticker_upkeep())
        self._loop.create_task(self._quote_change_upkeep())
        self._loop.create_task(self._balances_upkeep())
        self._loop.run_forever()

    # ----
    async def restart(self):
        await self.stop()

        self._loop = asyncio.get_event_loop()
        self._init_client_connection()
        self._loop.run_until_complete(self._client_async.load_markets())

        self.start()

    # ----
    async def stop(self):
        await self._client_async.close()

    # ----
    def update_balances(self):
        """
        sets and returns dict of balances as such:
        fetch balances from exchange.
        loop through balances, calculate bought price / total cost for each pair
        if we already own the pair calculate from previous bought price, else calculate from full history
        average calc dict format: {'total_cost': total_cost, 'amount': end_amount, 'avg_price': avg_price, 'last_id': last_buy_id}
        """

        balances = self._client.fetchBalance()
        for key in balances:
            if key == self.quote_currency:
                self.balance = balances[key]['total']
                continue

            symbol = key + '/' + self.quote_currency
            if symbol in self.pairs:
                amount = balances[key]['total']

                # if we already have average data, calculate from existing
                if symbol in self.pairs and self.pairs[symbol]['total_cost'] != 0:
                    if amount != self.pairs[symbol]['total']:
                        trades = self._client.fetchMyTrades(symbol)
                        # update free, used, total
                        self.pairs[symbol].update(balances[key])
                        # update with new average data
                        new_average_data = calc_average_price_from_hist(trades, amount)

                        if new_average_data is None:
                            self.pairs[symbol]['total_cost'] = None
                            self.pairs[symbol]['avg_price'] = None
                            self.pairs[symbol]['amount'] = None

                        else:
                            self.pairs[symbol].update(new_average_data)

                # if we don't have average data / trade history, add new
                else:
                    # skip wicked small values
                    if amount < self.pairs[symbol]['limits']['amount']['min']:
                        continue

                    # fetch trades for symbol from API
                    trades = self._client.fetchMyTrades(symbol)
                    # calculate average data
                    average_data = calc_average_price_from_hist(trades, amount)

                    if average_data is None:
                        # if we cant calculate teh avg, print out some datas to help with debugging
                        print('could not calculate average for: {}'.format(symbol))
                        print(self.pairs[symbol]['limits'])
                        print(self.pairs[symbol]['precision'])
                        print(amount)
                        continue

                    self.pairs[symbol].update(average_data)
                    self.pairs[symbol].update(balances[key])

                self.pairs[symbol]['total'] = amount
                self.pairs[symbol]['amount'] = amount

    # ----
    def _initialize_pairs(self):
        # TODO: Make async?
        pairs = {
                    x['symbol']: x
                    for x in self._client.fetchMarkets()
                    if x['active'] and x['quote'] == self.quote_currency.upper()
                }
        candles = {}
        for pair in pairs:
            # assign default values for pairs
            candles[pair] = {}
            pairs[pair]['total'] = 0
            pairs[pair]['amount'] = 0
            pairs[pair]['total_cost'] = 0
            pairs[pair]['avg_price'] = None
            pairs[pair]['dca_level'] = 0
            pairs[pair]['last_order_time'] = 0
            pairs[pair]['trades'] = []
            pairs[pair]['last_id'] = 0
            pairs[pair]['last_depth_check'] = 0

        self.pairs = pairs
        self.candles = candles
        return pairs

    # ----
    def place_order(self, symbol, order_type, side, amount, price):
        bought_price = self.pairs[symbol]['avg_price'] if side.lower() == 'sell' else None
        print(symbol, amount, self.pairs[symbol]['total'])
        order = self._client.create_order(symbol, order_type, side, self._client.amount_to_precision(symbol, amount), self._client.price_to_precision(symbol, price))
        print(order)

        if bought_price is not None:
            order['bought_price'] = bought_price

        if 'total' not in self.pairs[symbol]:
            self.pairs[symbol]['total'] = 0
        filled = order['filled']

        # fee will only be currency
        if self.pairs[symbol]['base'] == order['fee']['currency']:
            filled -= order['fee']['cost']

        # increment or decrement 'total' (quantity owned)
        self.pairs[symbol]['total'] += filled if side == 'buy' else - filled

        # increment or decrement total cost
        self.pairs[symbol]['total_cost'] += order['cost'] if side == 'buy' else - order['cost']

        # if we sell at a profit reset total cost to 0
        if self.pairs[symbol]['total_cost'] < 0:
            self.pairs[symbol]['total_cost'] = 0

        # recalculate average price from total cost and amount
        try:
            self.pairs[symbol]['avg_price'] = self.pairs[symbol]['total_cost'] / self.pairs[symbol]['total']
        except ZeroDivisionError:
            self.pairs[symbol]['avg_price'] = None

        # update quote balance
        self.balance += order['cost'] if side == 'buy' else - order['cost']
        # update last order time
        self.pairs[symbol]['last_order_time'] = int(time.time())
        # temp - will manually calc avg instead of calling update
        # self.update_balances()

        return order

    # ----
    def get_depth(self, symbol, side):
        """
        get bids or asks for pair. if side == buy, return asks, else bids.
        if the orderbook has been fetched too recently, return none
        :param symbol:
        :param side: buy/sell
        :return: list: bids/asks
        """
        pair = self.pairs[symbol]
        if time.time() - pair['last_depth_check'] > 0.5:
            depth = self._client.fetch_order_book(symbol)
            pair['last_depth_check'] = time.time()
            return depth['asks'] if side.upper() == 'BUY' else depth['bids']

        else:
            return None

    async def safe_fetch_ohlcv(self, symbol, timeframe, limit):
        counter = 0

        while counter < 10:
            try:
                return await self._client_async.fetchOHLCV(symbol, timeframe=timeframe, limit=limit)

            except Exception as ex:
                print(f'Got {ex} during safe_fetch_ohlcv(), retrying ({counter}/10)')

    # ----
    async def _get_candles(self, num_candles=1):
        """
        Create a list of symbol/timeframe tuples from self.pairs
        These will each be passed into a separate call to self.client_async.fetchOHLV below
        """

        args = [
                    (symbol, timeframe)
                    for timeframe in self._candle_timeframes
                    for symbol in self.pairs.keys()
               ]

        # Map the arguments to the fetchOHLCV using a lambda function to make
        # providing keyword args easier
        tasks = itertools.starmap(lambda s, t: self.safe_fetch_ohlcv(s, t, num_candles), args)

        # Wraps futures into a single coroutine
        task_group = asyncio.gather(*tasks)

        # Wait for all tasks to finish (executed asynchronously)
        await task_group

        return args, task_group.result()

    # --
    async def load_all_candle_histories(self, num_candles=500):
        args, results = await self._get_candles(num_candles)

        # Build our results from the results returned by the task_group coroutine we awaited before
        for (symbol, period), candlesticks in zip(args, results):
            self.candles[symbol][period] = candles_to_df(candlesticks)

        return self.pairs

    # --
    async def _candle_upkeep(self):
        """
        update candle history during runtime - see binance klines socket handler
        candle history will fetch most recent candle for all timeframes and assign to end of candles dataframe
        """

        while 1:
            args, results = await self._get_candles(1)

            for (symbol, timeframe), candle_data in zip(args, results):
                candle = candle_tic_to_df(*candle_data)
                self.candles[symbol][timeframe].loc[candle.index[0]] = candle.iloc[0]

            await asyncio.sleep(self._candle_upkeep_call_schedule)



    # --
    async def _quote_change_upkeep(self):
        """
        update candle history during runtime - see binance klines socket handler
        candle history will fetch most recent candle for all timeframes and assign to end of candles dataframe
        """

        while 1:
            if 'USD' in self.quote_currency:
                return

            quote_candles = await self._client_async.fetchOHLCV(self.quote_currency.upper() + '/USDT', timeframe='1h', limit=168)

            self.quote_candles = candles_to_df(quote_candles)
            self.quote_price = self.quote_candles.iloc[-1]['close']
            self.quote_change_info['1h'] = get_change_between_candles(self.quote_candles, 1)
            self.quote_change_info['4h'] = get_change_between_candles(self.quote_candles, 4)
            self.quote_change_info['6h'] = get_change_between_candles(self.quote_candles, 6)
            self.quote_change_info['12h'] = get_change_between_candles(self.quote_candles, 12)
            self.quote_change_info['24h'] = get_change_between_candles(self.quote_candles, 24)

            await asyncio.sleep(self._quote_change_upkeep_call_schedule)

    # --
    async def _balances_upkeep(self):
        """
        update candle history during runtime - see binance klines socket handler
        candle history will fetch most recent candle for all timeframes and assign to end of candles dataframe
        """

        while 1:
            self.update_balances()
            await asyncio.sleep(self._balance_upkeep_call_schedule)

    # ----
    async def _ticker_upkeep(self):
        """
        update ticker info during runtime - see binance ticker socket handler
        update pair['close'], pair['quoteVolume'], pair['percentage']
        may want to use either client.fetchTickers or client.fetchTicker(symbol)
        fetchTickers gets all so this should save api calls but there will be irrelevant data
        """

        while 1:
            tickers = await self._client_async.fetchTickers()

            for ticker_info in tickers.values():
                symbol = ticker_info['symbol']

                if symbol in self.pairs:
                    self.pairs[symbol].update(ticker_info)

            await asyncio.sleep(self._ticker_upkeep_call_schedule)

    def get_min_cost(self, symbol):
        return self.pairs[symbol]['limits']['cost']['min']

    def reload_single_candle_history(self, symbol):
        for period in self._candle_timeframes:
            candlesticks = self._client.fetchOHLCV(symbol, timeframe=period, limit=300)
            self.candles[symbol][period] = candles_to_df(candlesticks)


if __name__ == '__main__':
    ex = GenericExchange('bittrex',
                         'ETH',
                         {'public': '4fb9e3fe9e0e4c1eb80c82bb6126cf83',
                          'secret': '5942a5567e014fdfa05f0d202c5bec24'},
                         ['1m', '5m', '30m']
                         )

    print('Starting exchange')
    ex.initialize()
    # import threading
    # threading.Thread(target=ex.start()).start()
    print(ex.get_depth('ADA/ETH', 'buy'))
    print(ex.get_depth('ADA/ETH', 'buy'))
    print(ex.get_depth('ADA/ETH', 'buy'))
    time.sleep(1)
    print(ex.get_depth('ADA/ETH', 'buy'))
    """
    loop = asyncio.get_event_loop()

    loop.run_until_complete(ex.load_all_candle_histories())
    ex.pairs

    print('Running candle upkeep')
    for i in range(1, 1000):
        loop.run_until_complete(ex.candle_upkeep())

        loop.run_until_complete(ex.candle_upkeep())

        loop.run_until_complete(ex.candle_upkeep())
        time.sleep(2)

    ex.pairs

    loop.run_until_complete(ex.stop())
    """
