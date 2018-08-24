import asyncio
import typing

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
            'timeout': 10000,
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
        active_in_market = list(filter(lambda x: x['active'] and x['quote'] == quote_asset.upper(), self.client.fetchMarkets()))
        return {x['symbol']: x for x in active_in_market}

    # ----
    def place_order(self, symbol, order_type, side, amount, price):
        return self.client.create_order(symbol, order_type, side, amount, self.client.priceToPrecision(price))

    # ----
    def get_depth(self, symbol):
        return self.client.fetch_order_book(symbol)

    # ----
    async def load_all_candle_histories(self):
        async for (symbol, candles, period) in self.initialize_candle_history(list(self.pairs.keys())):
            print(symbol, candles)
            self.pairs[symbol]['candlesticks_{}'.format(period)] = candles
        return self.pairs

    # ----
    # will remove default timeframes later, just for ease of test
    async def initialize_candle_history(self, tickers, timeframes = ['5m', '1h', '1d'], num_candles = 100):
        i = 0
        while i < len(tickers):
            symbol = tickers[i % len(tickers)]
            for t in timeframes:
                yield (symbol, await self.client_async.fetchOHLCV(symbol, timeframe=t, limit=num_candles), t)
            i += 1
        await self.client_async.close()

    async def candle_upkeep(self, tickers, timeframes = ['5m', '1h', '1d'], num_candles = 100):
        i = 0

        while True:
            symbol = tickers[i % len(tickers)]
            for t in timeframes:
                yield (symbol, await self.client_async.fetchOHLCV(symbol, timeframe=t, limit=1))
            i += 1
            await asyncio.sleep(self.client_async.rateLimit / 1000)

    async def ticker_upkeep(self, tickers):
        i = 0

        while True:
            symbol = tickers[i % len(tickers)]
            print('--------------------------------------------------------------')
            print(self.client_async.iso8601(self.client_async.milliseconds()), 'fetching', symbol, 'ticker from', self.client_async.name)
            # this can be any call instead of fetch_ticker, really
            try:
                ticker = await self.client_async.fetch_ticker(symbol)
                print(self.client_async.iso8601(self.client_async.milliseconds()), 'fetched', symbol, 'ticker from', self.client_async.name)
                print(ticker)
            except ccxt.RequestTimeout as e:
                print('[' + type(e).__name__ + ']')
                print(str(e)[0:200])
                # will retry
            except ccxt.DDoSProtection as e:
                print('[' + type(e).__name__ + ']')
                print(str(e.args)[0:200])
                # will retry
            except ccxt.ExchangeNotAvailable as e:
                print('[' + type(e).__name__ + ']')
                print(str(e.args)[0:200])
                # will retry
            except ccxt.ExchangeError as e:
                print('[' + type(e).__name__ + ']')
                print(str(e)[0:200])
                break  # won't retry
            i+=1


if __name__ == '__main__':
    ex = BaseExchange('bittrex', {})
    ex.init_client_connection()

    ex.pairs = ex.get_pairs('ETH')
    print(ex.pairs)
    from timeit import default_timer as timer

    start = timer()
    # ...

    asyncio.get_event_loop().run_until_complete(ex.load_all_candle_histories())
    end = timer()
    print(end - start)