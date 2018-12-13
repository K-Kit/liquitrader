"""
This will take in a list of conditions
"""
import numpy
from talib import get_functions as get_talib_functions

talib_funcs = get_talib_functions()


class Condition:
    """
    Base class condition:
    Holds a dict of pairs, along with their floor/ceiling depending on condition type
    """

    def __init__(self, condition_config: dict, pair_settings=None):
        self.conditions_list = condition_config['conditions']
        if 'trailing %' in condition_config:
            self.trailing_value = float(condition_config['trailing %'])
        else:
            self.trailing_value = 0
        self.pairs_trailing = {}
        self.indicators = self.get_indicators()
        self.pair_settings = pair_settings

    def get_indicators(self):
        indicators = []
        for condition in self.conditions_list:
            for key, part in condition.items():
                if isinstance(part, dict):
                    if 'value' in part:
                        if part['value'] in talib_funcs:
                            period = 0 if "candle_period" not in part else part["candle_period"]
                            if isinstance(period, str) and period == '':
                                period = None
                            if period is not None and int(period) > 0:
                                indicators.append(
                                    "{}_{}_{}".format(part['value'], period, part['timeframe'])
                                )
                            else:
                                indicators.append(
                                    "{}_{}".format(part['value'], part['timeframe'])
                                )
        self.indicators = indicators
        return indicators

    @staticmethod
    def get_last(arr):
        return arr[len(arr) - 1]

    # ----
    def get_stats_list(self, stats_dict):
        stats = []
        for key, value in stats_dict.items():
            if key not in self.indicators:
                continue
            last_value = self.get_last(value)
            if numpy.isnan(last_value):
                print(key, last_value, value)
                continue
            else:
                stats.append([key, float(last_value)])
        return stats

    def trail_to(self, start, end, pair, indicators):
        return {'trail_from': round(start, 10),
                'trail_to': round(end, 10),
                **pair,
                "stats": self.get_stats_list(indicators)
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
