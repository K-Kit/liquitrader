import json

from analyzers.TechnicalAnalysis import ta_list

BUY_STRATEGY_PATH = 'config/BuyStrategies.json'
DCA_STRATEGY_PATH = 'config/DCABuyStrategies.json'
GENERAL_SETTINGS_PATH = 'config/GeneralSettings.json'
GLOBAL_TRADE_CONDITION_PATH = 'config/GlobalTradeConditions.json'
PAIR_SPECIFIC_SETTINGS_PATH = 'config/PairSpecificSettings.json'
SELL_STRATEGIES_PATH = 'config/SellStrategies.json'


class Config:

    def __init__(self):
        self.buy_strategies = None
        self.dca_buy_strategies = None
        self.sell_strategies = None
        self.general_settings = None
        self.pair_specific_settings = None
        self.global_trade_conditions = None
        self.timeframes = set()
        self.indicators = {}

    def load_buy_strategies(self):
        with open(BUY_STRATEGY_PATH, 'r') as f:
            self.buy_strategies = json.load(f)
        return self.buy_strategies

    def load_dca_buy_strategies(self):
        with open(DCA_STRATEGY_PATH, 'r') as f:
            self.dca_buy_strategies = json.load(f)
        return self.dca_buy_strategies

    def load_sell_strategies(self):
        with open(SELL_STRATEGIES_PATH, 'r') as f:
            self.sell_strategies = json.load(f)
        return self.sell_strategies

    def load_general_settings(self):
        with open(GENERAL_SETTINGS_PATH, 'r') as f:
            self.general_settings = json.load(f)

    def load_global_trade_conditions(self):
        with open(GLOBAL_TRADE_CONDITION_PATH, 'r') as f:
            self.global_trade_conditions = json.load(f)
            
    
    def update_buy_strategies(self, json_data):
        with open(BUY_STRATEGY_PATH, 'w') as f:
            json.dump(json_data, f)
            self.buy_strategies = json.loads(json_data)

    def update_dca_buy_strategies(self, json_data):
        with open(DCA_STRATEGY_PATH, 'w') as f:
            json.dump(json_data, f)
            self.dca_buy_strategies = json.loads(json_data)

    def update_sell_strategies(self, json_data):
        with open(SELL_STRATEGIES_PATH, 'w') as f:
            json.dump(json_data, f)
            self.sell_strategies = json.loads(json_data)

    def update_general_settings(self, json_data):
        with open(GENERAL_SETTINGS_PATH, 'w') as f:
            json.dump(json_data, f)
            self.general_settings = json.loads(json_data)

    def update_global_trade_conditions(self, json_data):
        with open(GLOBAL_TRADE_CONDITION_PATH, 'w') as f:
            json.dump(json_data, f)
            self.global_trade_conditions = json.loads(json_data)

    def parse_indicators_from_strategy(self, strategies):
        for strategy in strategies:
            for condition in strategy['conditions']:
                for key, part in condition.items():
                    if isinstance(part, dict):
                        if part['value'] in ta_list:
                            period = 0 if "candle_period" not in part else part["candle_period"]
                            indicator = { "name": part['value'], "candle_period": period}
                            # store in dict since we couldnt store a set of dicts
                            hashvalue = "{}{}".format(*indicator.values())
                            self.indicators[hashvalue] = indicator
                            self.timeframes.add(part['timeframe'])
        return self.indicators

    def load_all_strategies(self):
        self.parse_indicators_from_strategy(self.load_buy_strategies())

        self.parse_indicators_from_strategy(self.load_dca_buy_strategies())

        self.parse_indicators_from_strategy(self.load_sell_strategies())

        return self.indicators

    def get_indicators(self):
        return list(self.load_all_strategies().values())




if __name__ == '__main__':

    config = Config()
    strategies  = config.load_buy_strategies()
    indicators = config.parse_indicators_from_strategy(strategies)


