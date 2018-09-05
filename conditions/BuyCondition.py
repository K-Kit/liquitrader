from Condition import *

class BuyCondition(Condition):
    # "buy_value": 3,
    # "minimum_volume": 2,
    # "trailing %": 3
    def __init__(self, condition_config: dict):
        super().__init__(condition_config)
        self.buy_value = condition_config['buy_value']
        self.min_volume = condition_config['minimum_volume']

    def evaluate(self, pair: dict):
        """
        evaluate single pair against conditions
        if not in pairs_trailing and conditions = true : add to dict, set floor/ceiling at price -> return true
        else if conditions = false : remove from pairs_trailing -> return False
        else if in pairs_trailing and conditions = true and trail > trailing value: return amount to buy/sell
        :param pair:
        :return:
        """
        symbol = pair['symbol']
        price = pair['close']
        if True and symbol in self.pairs:
            current_marker = self.pairs_trailing[symbol]['trail_from']
            marker = price if price < current_marker else current_marker
            self.pairs_trailing[symbol] = {'trail_from':marker, 'trail_to': marker * (1 + (self.trailing_value/100))}
        elif True:
            self.pairs_trailing[symbol] = {'trail_from': price, 'trail_to': price * (1 + (self.trailing_value / 100))}
        elif False:
            self.pairs_trailing.pop(symbol)



if __name__ == '__main__':
    import json

    filename = '../config/config.json'
    with open(filename, 'r') as f:
        config = json.load(f)

    from pprint import pprint

    bs = config['general']['buy_strategies'][0]
    cond = BuyCondition(bs)
    print(vars(cond))