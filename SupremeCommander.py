"""
start exchange
every tic run technical analysis on pairs
after technical analysis check conditions
"""
import json

from exchanges import Binance

from analyzers.TechnicalAnalysis import run_ta

# test keys, trading disabled
from dev_keys_binance import keys

filename = 'config/config.json'
with open(filename, 'r') as f:
    config = json.load(f)

# timeframes is a placeholder, this will need to be parsed from buy/sell conditions
timeframes=['5m', '15m', '30m']

#also a placeholder same idea ^
indicators = {
        'MFI': {'name': 'MFI', 'candle_period': 0, 'lookback': None},
        'BBANDS': {'name': 'BBANDS', 'candle_period': 0, 'lookback': None},

    }

if config['exchange'].lower() == 'binance':
    exchange = Binance.BinanceExchange('binance', {'public': keys.public, 'secret': keys.secret})
else:
    # instantiate generic with exchange name lowercase
    pass


exchange.start(market=config['market'].upper(), timeframes=timeframes)

# run TA on exchange.pairs dict, assign indicator values to pair['indicators']
pairs = exchange.pairs
for pair in pairs:
    pairs[pair]['indicators'] = run_ta(pairs[pair]['candlesticks'], indicators)