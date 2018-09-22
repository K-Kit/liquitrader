"""
start exchange
every tic run technical analysis on pairs
after technical analysis check conditions
"""
import json

from exchanges import Binance

from analyzers.TechnicalAnalysis import run_ta
from conditions.BuyCondition import BuyCondition
from conditions.DCABuyCondition import DCABuyCondition
# test keys, trading disabled
from dev_keys_binance import keys

filename = 'config/config.json'
with open(filename, 'r') as f:
    config = json.load(f)

# timeframes is a placeholder, this will need to be parsed from buy/sell conditions
timeframes=['5m', '30m']

# also a placeholder same idea ^
indicators = {
        'MFI': {'name': 'MFI', 'candle_period': 0},
        'BBANDS': {'name': 'BBANDS', 'candle_period': 0},
        'MFI2': {'name': 'MFI', 'candle_period': 32},
        'BBANDS2': {'name': 'BBANDS', 'candle_period': 14},

    }

# statistics is a dict with key: symbol, values: indicators
statistics = {}

# dict to store strategy evaluations from
strategy_analysis = {}

# instantiate strategies
buy_strategies = []
for strategy in config['buy_strategies']:
    buy_strategies.append(BuyCondition(strategy))

dca_buy_strategies = []
for strategy in config['dca_buy_strategies']:
    dca_buy_strategies.append(DCABuyCondition(strategy))

if config['exchange'].lower() == 'binance':
    exchange = Binance.BinanceExchange('binance', 'ETH', {'public': keys.public, 'secret': keys.secret}, timeframes)
    # use USDT in tests to decrease API calls (only ~12 pairs vs 100+)

else:
    # instantiate generic with exchange name lowercase
    pass

exchange.initialize()
# exchange.start()

# run TA on exchange.pairs dict, assign indicator values to pair['indicators']
pairs = exchange.pairs
for pair in pairs:
    statistics[pair] = run_ta(pairs[pair]['candlesticks'], indicators)

import time
time.sleep(5)
for strategy in buy_strategies:
    for pair in pairs:
        # strategy.evaluate(pairs[pair],statistics[pair])
        if not strategy.evaluate(pairs[pair],statistics[pair]) is None:
            print(pair)
            print(strategy.evaluate(pairs[pair],statistics[pair]))

for strategy in dca_buy_strategies:
    for pair in pairs:
        # strategy.evaluate(pairs[pair],statistics[pair])
        if not strategy.evaluate(pairs[pair],statistics[pair]) is None:
            print(pair)
            print(strategy.evaluate(pairs[pair],statistics[pair]))