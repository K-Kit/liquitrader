import typing


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



    Returns
        Candlestick data
        Pair data
    """

    # ----
    def __init__(self, access_keys: typing.dict[str, str]):
        self.access_keys = access_keys

        self.client = None
        
    # ----
    def get_candlesticks(self):
        raise NotImplementedError

    # ----
    def get_pairs(self):
        raise NotImplementedError

    # ----
    def place_buy_order(self):
        raise NotImplementedError

    # ----
    def place_sell_order(self):
        raise NotImplementedError

    # ----
    def start(self):
        raise NotImplementedError

    # ----
    def stop(self):
        raise NotImplementedError
