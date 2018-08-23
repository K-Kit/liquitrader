import typing
import ccxt
import ccxt.async_support as ccxt_async
import asyncio
# will remove just for convenience right now

class keys:
    public_exchange_key = 'HPTpbOKj0konuPW72JozWGFDJbo0nK2rymbyObeX1vDSDSMZZd6vVosrA9dPFa1L'
    private_exchange_key = '4AuwPy6mVarrUqqECbyZSU9GrfOrInt6MIHdqvxHZWMaCXEjbSGGjBEuKmpCwPtb'
client = ccxt.binance
client_async = ccxt_async.binance

# set default options for binance
ccxt.binance().options['newOrderRespType'] = 'FULL'
ccxt.binance().options['defaultTimeInForce'] = 'IOC'
ccxt.binance().options['parseOrderToPrecision'] = True
ccxt.binance().options['recvWindow'] = 10000


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
    def __init__(self, exchange_id, access_keys: typing.DefaultDict[str, str]):
        self.access_keys = access_keys
        # initialize standard client
        self.pairs = {}
        exchange_class = getattr(ccxt, exchange_id)
        self.client = exchange_class({
            'apiKey': access_keys['public'],
            'secret': access_keys['secret'],
            'timeout': 30000,
            'enableRateLimit': True,
            'parseOrderToPrecision': True
        })
        # initialize async client
        exchange_class_async = getattr(ccxt_async, exchange_id)
        self.client_async = exchange_class_async({
            'apiKey': access_keys['public'],
            'secret': access_keys['secret'],
            'timeout': 30000,
            'enableRateLimit': True,
        })

    # ----
    def get_candlesticks(self, symbol, timeframe, since):
        return client.fetch_ohlcv(symbol, timeframe, since = None)

    # ----
    def get_pairs(self,quote_asset):
        active_in_market = list(filter(lambda x: x['active'] and x['quote'] == quote_asset.upper(), self.client.fetchMarkets()))
        return {x['symbol']: x for x in active_in_market}

    # ----
    def place_order(self, symbol, type, side, amount, price):
        return self.client.create_order(symbol, type, side, amount, self.client.priceToPrecision(price))


    def get_depth(self, symbol):
        return client.fetch_order_book(symbol)

    # ----
    def start(self):
        # this will be different for websocket /
        raise NotImplementedError

    # ----
    def stop(self):
        # stop fetching data, close sockets if applicable
        raise NotImplementedError

    async def initialize_candle_history(self, tickers):
        i = 0
        while True:
            symbol = tickers[i % len(tickers)]
            yield (symbol, await ex.client_async.fetchOHLCV(symbol,timeframe = '1d', limit = 3))
            i += 1
            # await asyncio.sleep(self.client_async.rateLimit / 1000)

    async def main(self):
        async for (symbol, candles) in self.initialize_candle_history(list(self.pairs.keys())):
            print(symbol, candles)
            self.pairs[symbol]['candlesticks'] = candles
        return self.pairs


if __name__ == '__main__':
    ex = BaseExchange('binance', {'public': keys.public_exchange_key, 'secret': keys.private_exchange_key})
    ex.pairs = ex.get_pairs('ETH')
    print(ex.pairs)
    asyncio.get_event_loop().run_until_complete(ex.main())