import asyncio
import typing
import itertools
from pprint import pprint

import ccxt
import ccxt.async_support as ccxt_async


class BaseExchange:
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
    def get_pairs(self,quote_asset):
        return {x['symbol']: x for x in (
                    filter(
                        lambda x: (x['active'] and x['quote'] == quote_asset.upper()),
                        self.client.fetchMarkets())
                    )
                }

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
            self.pairs[symbol]['candlesticks_{}'.format(period)] = candlesticks

        return self.pairs

    # --
    async def candle_upkeep(self, tickers, timeframes=None):
        """

        :param tickers:
        :param timeframes:
        :param num_candles:
        :return:
        """

        if timeframes is None:
            timeframes = ['5m', '1h', '1d']

        tickers_len = len(tickers)

        i = 0
        while 1:
            symbol = tickers[i % tickers_len]

            for t in timeframes:
                yield (symbol, await self.client_async.fetchOHLCV(symbol, timeframe=t, limit=1))

            await asyncio.sleep(self.client_async.rateLimit / 1000)

            i += 1

    # ----
    async def ticker_upkeep(self, tickers):
        tickers_len = len(tickers)

        i = 0
        while 1:
            #
            symbol = tickers[i % tickers_len]

            print('--------------------------------------------------------------')
            print(self.client_async.iso8601(self.client_async.milliseconds()), 'fetching', symbol, 'ticker from', self.client_async.name)

            # this can be any call instead of fetch_ticker, really
            try:
                ticker = await self.client_async.fetch_ticker(symbol)
                print(self.client_async.iso8601(self.client_async.milliseconds()), 'fetched', symbol, 'ticker from', self.client_async.name)
                print(ticker)

                i += 1

            except (ccxt.RequestTimeout, ccxt.DDoSProtection,ccxt.ExchangeNotAvailable) as e:
                pass  # will retry

            except ccxt.ExchangeError as e:
                break  # won't retry


if __name__ == '__main__':
    ex = BaseExchange('bittrex', {})
    ex.init_client_connection()

    ex.pairs = ex.get_pairs('ETH')
    from timeit import default_timer as timer

    start = timer()
    # ...

    asyncio.get_event_loop().run_until_complete(ex.load_all_candle_histories())

    print(len(ex.pairs))

    end = timer()
    print(end - start)
