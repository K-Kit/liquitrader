from conditions.Condition import Condition
from conditions.condition_tools import evaluate_condition
from utils.Utils import get_current_value, get_percent_change

class SellCondition(Condition):

    def __init__(self, condition_config: dict):
        super().__init__(condition_config)
        self.sell_value = condition_config['sell_value']

    def get_lowest_sell_price(self, total_cost, amount):
        bought_price = total_cost/amount
        return bought_price * (1 + (self.sell_value/100))

    def evaluate(self, pair: dict, indicators: dict, balance: float=None):
        """
        evaluate single pair against conditions
        if not in pairs_trailing and conditions = true : add to dict, set floor/ceiling at price -> return true
        else if conditions = false : remove from pairs_trailing -> return False
        else if in pairs_trailing and conditions = true and trail > trailing value: return amount to buy/sell
        :param pair:
        :return:
        """
        symbol = pair['symbol']
        if 'total' not in pair or 'close' not in pair or 'total_cost' not in pair:
            return None

        price = float(pair['close'])
        trail_to = None
        current_value = get_current_value(price, pair['total'])
        percent_change = get_percent_change(current_value, pair['total_cost'])
        analysis = [evaluate_condition(condition, pair, indicators, is_buy=False) for condition in self.conditions_list]

        # check percent change, if above trigger return none
        res = False not in analysis and percent_change > self.sell_value

        if res and symbol in self.pairs_trailing:
            current_marker = self.pairs_trailing[symbol]['trail_from']
            marker = price if price > current_marker else current_marker
            trail_to = marker * (1 - (self.trailing_value/100))
            self.pairs_trailing[symbol] = {'trail_from':marker, 'trail_to':trail_to }

        elif res:
            trail_to = price * (1 - (self.trailing_value / 100))
            self.pairs_trailing[symbol] = {'trail_from': price, 'trail_to':trail_to}

        elif not res:
            if symbol in self.pairs_trailing: self.pairs_trailing.pop(symbol)
            return None

        if price <= trail_to and not trail_to is None:
            return self.get_lowest_sell_price(pair['total_cost'], pair['total'])


if __name__ == '__main__':
    from examples import *
    strategy = {}
    # 1 and 3 are true with the test data
    strategy['conditions'] = [condition_1]
    strategy['trailing %'] = 0.1
    strategy['sell_value'] = 1
    pair1['total_cost'] = 1
    pair1['total'] = 1
    cond = SellCondition(strategy)
    print(vars(cond))
    print(cond.evaluate(pair1,indicators1))
    print(cond.pairs_trailing)
    pair1['close'] = 1

    print(cond.evaluate(pair1,indicators1))
    print(cond.pairs_trailing)

    pair1['close'] = 1.3

    print(cond.evaluate(pair1,indicators1))
    print(cond.pairs_trailing)

    pair1['close'] = 1.1

    print(cond.evaluate(pair1,indicators1))
    print(cond.pairs_trailing)