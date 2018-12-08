"""
This will take in a list of conditions
"""


class Condition:
    """
    Base class condition:
    Holds a dict of pairs, along with their floor/ceiling depending on condition type
    """

    def __init__(self, condition_config: dict):
        self.conditions_list = condition_config['conditions']
        self.trailing_value = condition_config['trailing %']
        self.pairs_trailing = {}

    @staticmethod
    def trail_to(start, end, pair, indicators):
        import numpy as np
        return {'trail_from': round(start, 10),
                'trail_to': round(end, 10),
                **pair,
                "stats": list(map(lambda x:
                                  [x[0],
                                       round(float(x[1][len(x)-1]), 8) if np.isfinite(x[1][len(x)-1]) else None
                                   ],
                                  indicators.items()))
                }

    def evaluate(self, pair: dict, indicators: dict, balance):
        """
        evaluate single pair against conditions
        if not in pairs_trailing and conditions = true : add to dict, set floor/ceiling at price -> return true
        else if conditions = false : remove from pairs_trailing -> return False
        else if in pairs_trailing and conditions = true and trail > trailing value: return amount to buy/sell
        :param pair:
        :return:
        """
        pass

    def update_trail_data(self, pairs):
        """
        Update pairs_trailing dict information:
        for buy condition 'if price < floor then floor = price'
        same idea with ceiling for sales
        :return: dict
        """
        pass

if __name__ == '__main__':
    from examples import *
    strategy = {}
    # 1 and 3 are true with the test data
    strategy['conditions'] = [condition_1, condition_3]
    strategy['trailing %'] = 0.1
    cond = Condition(strategy)
    print(vars(cond))
