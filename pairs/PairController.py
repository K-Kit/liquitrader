class PairController:

    def __init__(self, default_conditions=None):
        self.default_conditions = default_conditions
        self.pairs = {}

    # ----
    def add_pair(self, name, symbol, price, current_value, volumne, spread, change24, bids, asks,
                       bought_time, bought_price, bought_value, percent_change, tick_size, step_size):

        pair = {
            'name': 'ETH',
            'symbol': 'ETHUSD',

            'price': '',            # price per coin
            'current_value': '',    # amount_owned * price
            'volume': '',           # Amount of symbol that's been in past 24h

            'spread': '',
            'change24': '',

            'bids': '',
            'asks': '',

            'bought_time': '',
            'bought_price': '',
            'bought_value': '',

            'percent_change': '',

            'tick_size': '',
            'step_size': '',

            'candle_history': '',

            'conditions': [],

            'current_condition_values': []  # For front-end simplicity
        }

        self.pairs[name] = pair

    # ----
    def get_pair(self, name=None, symbol=None):
        if symbol is not None:
            name = symbol[:3] # get name from symbol

        elif name is None:
            return False

        return self.pairs[name]

    # --
    def get_pairs(self):
        return self.pairs

    # ----



