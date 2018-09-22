from Condition import Condition
from condition_tools import evaluate_condition

class BuyCondition(Condition):

    def __init__(self, condition_config: dict):
        super().__init__(condition_config)
        self.buy_value = condition_config['buy_value']

    def evaluate(self, pair: dict, indicators: dict):
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
        trail_to = None
        analysis = [evaluate_condition(condition, pair, indicators) for condition in self.conditions_list]
        print(analysis)
        res = False not in analysis
        if res and symbol in self.pairs_trailing:
            current_marker = self.pairs_trailing[symbol]['trail_from']
            marker = price if price < current_marker else current_marker
            trail_to = marker * (1 + (self.trailing_value/100))
            self.pairs_trailing[symbol] = {'trail_from':marker, 'trail_to':trail_to }
        elif res:
            trail_to = price * (1 + (self.trailing_value / 100))
            self.pairs_trailing[symbol] = {'trail_from': price, 'trail_to':trail_to}
        elif not res:
            if symbol in self.pairs_trailing: self.pairs_trailing.pop(symbol)
            return None
        if price >= trail_to and not trail_to is None:
            return self.buy_value*price


if __name__ == '__main__':
    from testconditions import *
    strategy = {}
    # 1 and 3 are true with the test data
    strategy['conditions'] = [condition_2, condition_3]
    strategy['trailing %'] = 0.1
    strategy['buy_value'] = 0.02
    cond = BuyCondition(strategy)
    print(vars(cond))
    print(cond.evaluate(pair1,indicators1))
    print(cond.pairs_trailing)
    pair1['close'] = 4.005

    print(cond.evaluate(pair1,indicators1))
    print(cond.pairs_trailing)

    pair1['close'] = 4.1

    print(cond.evaluate(pair1,indicators1))
    print(cond.pairs_trailing)