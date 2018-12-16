from conditions.Condition import Condition
from conditions.condition_tools import evaluate_condition, get_buy_value

class BuyCondition(Condition):

    def __init__(self, condition_config: dict, pair_settings=None):
        super().__init__(condition_config, pair_settings)
        self.buy_value = condition_config['buy_value']

    def apply_pair_settings(self, pair, balance):
        pair_settings = self.pair_settings
        id = pair.split("/")[0]
        if pair_settings is None or id not in pair_settings or "buy" not in pair_settings[id]:
            return get_buy_value(self.buy_value, balance)

        elif pair_settings[id]["buy"]["method"] == "modify":
            return float(pair_settings[id]["buy"]["value"]) * get_buy_value(self.buy_value, balance)
        elif pair_settings[id]["buy"]["method"] == "override":
            return get_buy_value(pair_settings[id]["buy"]["value"], balance)



    def evaluate(self, pair: dict, indicators: dict, balance):
        """
        evaluate single pair against conditions
        if not in pairs_trailing and conditions = true : add to dict, set floor/ceiling at price -> return true
        else if conditions = false : remove from pairs_trailing -> return False
        else if in pairs_trailing and conditions = true and trail > trailing value: return amount to buy/sell
        :param balance:
        :param indicators:
        :param pair:
        :return:
        """
        symbol = pair['symbol']
        if symbol is None:
            print(pair)
            return None
        if 'close' not in pair:
            return None

        price = float(pair['close'])
        trail_to = None
        analysis = [evaluate_condition(condition, pair, indicators) for condition in self.conditions_list]
        res = False not in analysis

        if res and symbol in self.pairs_trailing:
            current_marker = self.pairs_trailing[symbol]['trail_from']
            marker = price if price < current_marker else current_marker
            trail_to = marker * (1 + (self.trailing_value / 100))
            self.pairs_trailing[symbol] = self.trail_to(marker, trail_to, pair, indicators)

        elif res:
            trail_to = price * (1 + (self.trailing_value / 100))
            self.pairs_trailing[symbol] = self.trail_to(price, trail_to, pair, indicators)

        elif not res:
            if symbol in self.pairs_trailing: self.pairs_trailing.pop(symbol)
            return None

        if price >= trail_to and not trail_to is None:
            return self.apply_pair_settings(symbol, balance) / price


if __name__ == '__main__':
    from conditions.examples import *

    strategy = {}
    # 1 and 3 are true with the test data
    strategy['conditions'] = [condition_2, condition_3]
    strategy['trailing %'] = 0.1
    strategy['buy_value'] = '200%'
    cond = BuyCondition(strategy)
    print(vars(cond))
    print(cond.evaluate(pair1, indicators1, 1))
    print(cond.pairs_trailing)
    pair1['close'] = 4.005

    print(cond.evaluate(pair1, indicators1, 1))
    print(cond.pairs_trailing)

    pair1['close'] = 4.1

    print(cond.evaluate(pair1, indicators1, 1))
    print(cond.pairs_trailing)
    print(vars(cond))
    print(vars(cond))
