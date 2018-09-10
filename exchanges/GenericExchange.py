import asyncio
import typing
import itertools
from pprint import pprint
import time

import ccxt
import ccxt.async_support as ccxt_async

from utils.CandleTools import candles_to_df
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
    def __init__(self, exchange_id, access_keys: typing.Dict[str, str]):
        self.access_keys = access_keys
        self.pairs = {}

        # initialize standard and sync client
        self.exchange_class = getattr(ccxt, exchange_id)
        self.exchange_class_async = getattr(ccxt_async, exchange_id)

        self.client = None
        self.client_async = None
        self.balances = None
        self.tickers = []

    # ----
    def init_client_connection(self):
        # initialize synchronous client

        self.client = self.exchange_class({
            'apiKey': self.access_keys['public'],
            'secret': self.access_keys['secret'],
            'timeout': 30000,
            'enableRateLimit': True,
            'parseOrderToPrecision': True
        })

        # initialize async client
        self.client_async = self.exchange_class_async({
            'apiKey': self.access_keys['public'],
            'secret': self.access_keys['secret'],
            'timeout': 30000,
            'enableRateLimit': False
        })

    # ----
    def initialize_market(self):
        pass

    # ----
    def start(self):
        # this will be different for websocket /
        raise NotImplementedError

    # ----
    def stop(self):
        # stop fetching data, close sockets if applicable
        raise NotImplementedError

    # ----
    def get_candlesticks(self, symbol, timeframe, since):
        return self.client_async.fetch_ohlcv(symbol, timeframe)

    # ----
    def update_balances(self):
        # sets and returns dict of balances as such:
        # 'BTC': {'free': 0.0, 'used': 0.0, 'total': 0.0},
        # 'LTC': {'free': 0.0, 'used': 0.0, 'total': 0.0},
        # these will be accessible as balances[pairs[pair_name]['base']]
        self.balances = self.client.fetchBalance()
        return self.balances

    # ----
    def get_pairs(self,quote_asset):
        pairs = {x['symbol']: x for x in (
                    filter(
                        lambda x: (x['active'] and x['quote'] == quote_asset.upper()),
                        self.client.fetchMarkets())
                    )
                }
        for pair in pairs:
            pairs[pair]['candlesticks'] = {}
        self.pairs = pairs
        return pairs

    # ----
    def place_order(self, symbol, order_type, side, amount, price):
        return self.client.create_order(symbol, order_type, side, amount, self.client.priceToPrecision(price))

    # ----
    def get_depth(self, symbol):
        return self.client.fetch_order_book(symbol)

    # ----
    async def load_all_candle_histories(self, timeframes=None, num_candles=100):

        # Don't use lists as default arguments -- things can get real weird, real fast.
        timeframes = ['5m', '1h', '1d'] if timeframes is None else timeframes

        # Create a list of symbol/timeframe tuples from self.pairs
        # These will each be passed into a separate call to self.client_async.fetchOHLV below
        args = [(symbol, t) for t in timeframes for symbol in self.pairs.keys()]

        # Map the arguments to the fetchOHLCV using a lambda function to make
        # providing keyword args easier
        tasks = itertools.starmap(lambda s, t: self.client_async.fetchOHLCV(s, timeframe=t, limit=num_candles), args)

        # Wraps futures into a single coroutine
        task_group = asyncio.gather(*tasks)

        # Wait for all tasks to finish (executed asynchronously)
        await task_group

        # Appease the ccxt gods
        await self.client_async.close()

        # Build our results from the results returned by the task_group coroutine we awaited before
        for (symbol, period), candlesticks in zip(args, task_group.result()):
            self.pairs[symbol]['candlesticks'][period] = candles_to_df(candlesticks)
        time.sleep(1)
        return self.pairs

    # ----
    async def candle_upkeep(self, tickers, timeframes=None):
        # update candle history during runtime - see binance klines socket handler
        # candle history will fetch most recent candle for all timeframes and assign to end of candles dataframe
        # use Utils.candletools.candle_tic_to_df()
        # self.client.fetchOHLCV(symbol, timeframe=timeframe, limit=1)

        raise NotImplementedError

    # ----
    async def ticker_upkeep(self, tickers):
        # update ticker info during runtime - see binance ticker socket handler
        # update pair['close'], pair['quoteVolume'], pair['percentage']
        # may want to use either client.fetchTickers or client.fetchTicker(symbol)
        # fetchTickers gets all so this should save api calls but there will be irrelevant data

        raise NotImplementedError

    # ----
    async def depth_upkeep(self, tickers):
        # update depth info during runtime - see binance depth socket handler
        # this only needs to actually be preformed on pairs we are trailing / trying to buy
        # can do on all if api allows / is significantly easier
        # update pair['bids] and pair['asks'] in form [ [price, amount] ] (it should already be like this in ccxt
        # self.client.fetchOrderBook(pair)

        raise NotImplementedError


if __name__ == '__main__':
    ex = GenericExchange('bittrex', {'public': '4fb9e3fe9e0e4c1eb80c82bb6126cf83',
                                     'secret': '5942a5567e014fdfa05f0d202c5bec24'})
    ex.init_client_connection()

    ex.pairs = ex.get_pairs('ETH')
    from timeit import default_timer as timer

    start = timer()
    # ...

    asyncio.get_event_loop().run_until_complete(ex.load_all_candle_histories())

    print(len(ex.pairs))

    end = timer()
    print(end - start)
