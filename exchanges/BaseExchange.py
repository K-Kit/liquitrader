import typing
import ccxt
import ccxt.async_support as ccxt_async


# will remove just for convenience right now
class keys:
    public_exchange_key = 'HPTpbOKj0konuPW72JozWGFDJbo0nK2rymbyObeX1vDSDSMZZd6vVosrA9dPFa1L'
    private_exchange_key = '4AuwPy6mVarrUqqECbyZSU9GrfOrInt6MIHdqvxHZWMaCXEjbSGGjBEuKmpCwPtb'


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
            'timeout': 30000,
            'enableRateLimit': True
        })

    # ---
    def get_candlesticks(self, symbol, timeframe, since):
        return self.client_async.fetch_ohlcv(symbol, timeframe, since=None)

    # ----
    def get_pairs(self):
        return self.client.fetchMarkets()

    # ----
    def place_order(self, symbol, type, side, amount, price):
        return self.client.create_order(symbol, type, side, amount, self.client.priceToPrecision(price))

    # ----
    def get_depth(self, symbol):
        return self.client.fetch_order_book(symbol)

    # ----
    def start(self):
        # this will be different for websocket /
        raise NotImplementedError

    # ----
    def stop(self):
        # stop fetching data, close sockets if applicable
        raise NotImplementedError


if __name__ == '__main__':
    ex = BaseExchange('binance', {'public': keys.public_exchange_key, 'secret': keys.private_exchange_key})
    ex.pairs = ex.get_pairs()