"""
start exchange
every tic run technical analysis on pairs
after technical analysis check conditions
"""
import json
from functools import reduce

from exchanges import Binance

from exchanges import PaperBinance
from analyzers.TechnicalAnalysis import run_ta
from conditions.BuyCondition import BuyCondition
from conditions.DCABuyCondition import DCABuyCondition
from conditions.SellCondition import SellCondition
from utils.Utils import *
from conditions.condition_tools import *

# test keys, trading disabled
from dev_keys_binance import keys

filename = 'config/config.json'
with open(filename, 'r') as f:
    config = json.load(f)

DUST_VALUE = 0.02

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


sell_strategies = []
for strategy in config['sell_strategies']:
    sell_strategies.append(SellCondition(strategy))

#temp
config['starting_balance'] = 10

if config['exchange'].lower() == 'binance':
    exchange = PaperBinance.PaperBinance('binance', 'ETH',config['starting_balance'], {'public': keys.public, 'secret': keys.secret}, timeframes)
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

owned = []
# return total current value (pairs + balance)
def get_tcv():
    pending = 0
    global owned
    owned = []
    for pair, value in exchange.pairs.items():
        if 'total' not in value or 'close' not in value: continue
        pending+= value['close'] * value['total']
        if value['close'] * value['total'] > 0:
            owned.append(pair)
    return pending + exchange.balance

def get_possible_buys(pairs, strategies):
    possible_trades = {}
    tcv = get_tcv()
    for strategy in strategies:
        for pair in pairs:
            # strategy.evaluate(pairs[pair],statistics[pair])
            result = strategy.evaluate(pairs[pair], statistics[pair], tcv)
            if not result is None:
                # print('{}: {}'.format(pair,result))
                if pair not in possible_trades or possible_trades[pair] > result:
                    possible_trades[pair] = result
        return possible_trades

def get_possible_sells(pairs, strategies):
    possible_trades = {}
    for strategy in strategies:
        for pair in pairs:
            # strategy.evaluate(pairs[pair],statistics[pair])
            result = strategy.evaluate(pairs[pair], statistics[pair])
            if not result is None:
                # print('{}: {}'.format(pair, result))
                if pair not in possible_trades or possible_trades[pair] < result:
                    possible_trades[pair] = result
        return possible_trades


def pair_specific_buy_checks(pair, price, amount, balance, change):
    min_balance = config['min_buy_balance'] if not isinstance(config['min_buy_balance'], str) \
        else percentToFloat(config['min_buy_balance']) * get_tcv()
    return all(
        [not exceeds_min_balance(balance, min_balance,price, amount),
        below_max_change(change, config['max_change']),
        above_min_change(change, config['min_change']),
        not is_blacklisted(pair, config['blacklist']),
        is_whitelisted(pair, config['whitelist']),
        exchange.pairs[pair]['total'] < 0.8 * amount
        ]
    )

def global_buy_checks():
    # todo add 1h change + max pairs
    #quote change 24h
    above_min_change(exchange.quote_change, config['market_change']['min_24h_quote_change'])
    below_max_change(exchange.quote_change, config['market_change']['max_24h_quote_change'])

    # # quote change 1h
    # above_min_change()
    # below_max_change()
    #
    # # average change 24h
    # above_min_change()
    # below_max_change()
    #
    # below_max_pairs()

# check min balance, max pairs, quote change, market change, trading enabled, blacklist, whitelist, 24h change
# todo add pair specific settings
def handle_possible_buys(possible_buys):
    for pair in possible_buys:
        if pair_specific_buy_checks(pair, exchange.pairs[pair]['close'], possible_buys[pair], exchange.balance, exchange.pairs[pair]['percentage']):
            order = exchange.place_order(pair, 'limit', 'buy', possible_buys[pair], exchange.pairs[pair]['close'])
            print(order)
            print(exchange.balance, get_tcv())
            print(pairs[pair]['total']*pairs[pair]['close'])

sales = []
def handle_possible_sells(possible_sells):
    global sales
    for pair in possible_sells:
        if exchange.pairs[pair]['total'] * exchange.pairs[pair]['amount'] < DUST_VALUE: continue
        order = exchange.place_order(pair, 'limit', 'sell', exchange.pairs[pair]['amount'], possible_sells[pair])
        sales.append(order)
        print(order)
        print(exchange.balance, get_tcv())
        print(pairs[pair]['total'] * pairs[pair]['close'])


possible_buys = get_possible_buys(exchange.pairs, buy_strategies)
possible_dca_buys = get_possible_buys(exchange.pairs, dca_buy_strategies)
possible_sells = get_possible_sells(exchange.pairs, sell_strategies)


if __name__ == '__main__':
    for i in range(1, 10000):
        print("balance: {}, TCV: {}".format(exchange.balance, get_tcv()))
        possible_buys = get_possible_buys(exchange.pairs, buy_strategies)
        handle_possible_buys(possible_buys)
        possible_dca_buys = get_possible_buys(exchange.pairs, dca_buy_strategies)
        possible_sells = get_possible_sells(exchange.pairs, sell_strategies)
        handle_possible_sells(possible_sells)
        print(owned, sales)
        time.sleep(1)
        print(i)
        i+=1
