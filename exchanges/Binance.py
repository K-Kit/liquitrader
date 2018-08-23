from .BaseExchange import *



class BinanceExchange(BaseExchange):

    def __init__(self):
        super().__init__(exchange_id=None, access_keys=typing.Dict[str, str])
