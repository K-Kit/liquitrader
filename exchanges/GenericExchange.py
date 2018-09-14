import asyncio
import typing
import itertools
import time

import ccxt
import ccxt.async_support as ccxt_async

from utils.CandleTools import candles_to_df, candle_tic_to_df

# TODO filter pairs for min volume and blacklist
# TODO update balances on start before filter, if below min volume and not blacklisted still fetch if owned
# TODO on update balance check if balances not none, then if balances[id][total] != new balance, fetch trades for pair

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
                 access_keys: typing.Dict[typing.Union[str, str], typing.Union[str, str]],
                 candle_timeframes: typing.List[str]):

        self.pairs = {}
        self._balances = None

        self._access_keys = access_keys

        self._quote_currency = quote_currency.upper()  # second part of currency pair
        self._candle_timeframes = candle_timeframes

        # initialize standard and sync client
        self._exchange_class = getattr(ccxt, exchange_id)
        self._exchange_class_async = getattr(ccxt_async, exchange_id)

        self._client = None
        self._client_async = None

        self._loop = asyncio.get_event_loop()

        self._ticker_upkeep_call_schedule = 1  # Call ticker_upkeep() every 1s
        self._candle_upkeep_call_schedule = 5  # Call candle_upkeep() every 5s

        # Connect to exchange
        self._init_client_connection()

    # ----
    @property
    def balances(self):
        return self._balances

    # ----
    def _init_client_connection(self):
        # initialize synchronous client

        self._client = self._exchange_class({
            'apiKey': self._access_keys['public'],
            'secret': self._access_keys['secret'],
            'timeout': 50000,
            'enableRateLimit': True,
            'parseOrderToPrecision': True
        })

        # initialize async client
        self._client_async = self._exchange_class_async({
            'apiKey': self._access_keys['public'],
            'secret': self._access_keys['secret'],
            'timeout': 50000,
            'enableRateLimit': False
        })

    # ----
    def initialize(self):
        # Mandatory to call this before any other calls are made to Bittrex
        self._loop.run_until_complete(self._client_async.load_markets())
        self._initialize_pairs()

    # ----
    def start(self):
        self._loop.call_later(self._ticker_upkeep_call_schedule, self._ticker_upkeep)
        self._loop.call_later(self._candle_upkeep_call_schedule, self._candle_upkeep)
        self._loop.run_forever()

    # ----
    def restart(self):
        self.stop()

        self._loop = asyncio.get_event_loop()
        self._init_client_connection()
        self._loop.run_until_complete(self._client_async.load_markets())

        self.start()

    # ----
    async def stop(self):
        self._loop.close()
        await self._client_async.close()

    # ----
    def update_balances(self):
        """
        sets and returns dict of balances as such:

        'BTC': {'free': 0.0, 'used': 0.0, 'total': 0.0},
        'LTC': {'free': 0.0, 'used': 0.0, 'total': 0.0},

        these will be accessible as balances[pairs[pair_name]['base']]
        """

        self._balances = self._client.fetchBalance()
        return self.balances

    # ----
    def _initialize_pairs(self):
        # TODO: Make async?
        pairs = {
                    x['symbol']: x
                    for x in self._client.fetchMarkets()
                    if x['active'] and x['quote'] == self._quote_currency.upper()
                }

        for pair in pairs:
            pairs[pair]['candlesticks'] = {}

        self.pairs = pairs

        return pairs

    # ----
    def place_order(self, symbol, order_type, side, amount, price):
        return self._client.create_order(symbol, order_type, side, amount, self._client.priceToPrecision(price))

    # ----
    def get_depth(self, symbol):
        return self._client.fetch_order_book(symbol)

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
        tasks = itertools.starmap(lambda s, t: self._client_async.fetchOHLCV(s, timeframe=t, limit=num_candles), args)

        # Wraps futures into a single coroutine
        task_group = asyncio.gather(*tasks)

        # Wait for all tasks to finish (executed asynchronously)
        await task_group

        return args, task_group.result()

    # --
    async def load_all_candle_histories(self, num_candles=100):
        args, results = await self._get_candles(num_candles)

        # Build our results from the results returned by the task_group coroutine we awaited before
        for (symbol, period), candlesticks in zip(args, results):
            self.pairs[symbol]['candlesticks'][period] = candles_to_df(candlesticks)

        return self.pairs

    # --
    async def _candle_upkeep(self):
        """
        update candle history during runtime - see binance klines socket handler
        candle history will fetch most recent candle for all timeframes and assign to end of candles dataframe
        """

        args, results = await self._get_candles(1)

        for (symbol, timeframe), candle_data in zip(args, results):
            candle = candle_tic_to_df(candle_data)
            self.pairs[symbol]['candlesticks'][timeframe].loc[candle.index[0]] = candle.iloc[0]

        self._loop.call_later(self._candle_upkeep_call_schedule, self._candle_upkeep)

    # ----
    async def _ticker_upkeep(self):
        """
        update ticker info during runtime - see binance ticker socket handler
        update pair['close'], pair['quoteVolume'], pair['percentage']
        may want to use either client.fetchTickers or client.fetchTicker(symbol)
        fetchTickers gets all so this should save api calls but there will be irrelevant data
        """

        async for symbol, ticker_info in await self._client_async.fetchTickers():
            if symbol in self.pairs:
                self.pairs[symbol].update(ticker_info)

        self._loop.call_later(self._ticker_upkeep_call_schedule, self._ticker_upkeep)


if __name__ == '__main__':
    ex = GenericExchange('bittrex',
                         'USDT',
                         {'public': '4fb9e3fe9e0e4c1eb80c82bb6126cf83',
                          'secret': '5942a5567e014fdfa05f0d202c5bec24'},
                         ['1m', '5m', '15m']
                         )

    print('Starting exchange')
    ex.start()

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

