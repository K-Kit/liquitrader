from .BaseExchange import *


# set default options for binance
ccxt.binance.options['newOrderRespType'] = 'FULL'
ccxt.binance.options['defaultTimeInForce'] = 'IOC'
ccxt.binance.options['parseOrderToPrecision'] = True
ccxt.binance.options['recvWindow'] = 10000


class BinanceExchange(BaseExchange):

    def __init__(self):
        super().__init__(exchange_id=None, access_keys=typing.Dict[str, str])
