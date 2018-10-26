"""
start exchange
every tic run technical analysis on pairs
after technical analysis check conditions
"""
import json
from functools import reduce

import pandas as pd

from exchanges import BinanceExchange
from utils.DepthAnalyzer import *

from exchanges import PaperBinance
from analyzers.TechnicalAnalysis import run_ta
from conditions.BuyCondition import BuyCondition
from conditions.DCABuyCondition import DCABuyCondition
from conditions.SellCondition import SellCondition
from utils.Utils import *
from conditions.condition_tools import get_buy_value, percentToFloat

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
config['starting_balance'] = 1000

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

def do_technical_analysis():
    for pair in pairs:
        statistics[pair] = run_ta(exchange.candles[pair], indicators)

import time
time.sleep(5)
trade_history = []
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
                if pair not in possible_trades or possible_trades[pair] < result:
                    possible_trades[pair] = result
        return possible_trades


def pair_specific_buy_checks(pair, price, amount, balance, change, min_balance, dca = False):
    min_balance = min_balance if not isinstance(min_balance, str) \
        else percentToFloat(min_balance) * get_tcv()
    checks = [not exceeds_min_balance(balance, min_balance,price, amount),
        below_max_change(change, config['max_change']),
        above_min_change(change, config['min_change']),
        not is_blacklisted(pair, config['blacklist']),
        is_whitelisted(pair, config['whitelist'])
        ]
    if not dca:
        checks.append(exchange.pairs[pair]['total'] < 0.8 * amount)
        checks.append(below_max_pairs(len(owned), config['max_pairs']))
    return all(checks)


def global_buy_checks():
    # todo add 1h change + max pairs
    check_24h_quote_change = in_range(exchange.quote_change_info['24h'], config['market_change']['min_24h_quote_change'],
                                config['market_change']['max_24h_quote_change'])

    check_1h_quote_change = in_range(exchange.quote_change_info['1h'], config['market_change']['min_1h_quote_change'],
                                config['market_change']['max_1h_quote_change'])
    

    check_24h_market_change = in_range(get_average_market_change(pairs), config['market_change']['min_24h_market_change'],
                                config['market_change']['max_24h_market_change'])

    return all([
        check_1h_quote_change,
        check_24h_market_change,
        check_24h_quote_change
    ])




def check_for_viable_trade(current_price, orderbook, remaining_amount, min_cost, max_spread, dca = False):
    can_fill, minimum_fill = process_depth(orderbook, remaining_amount, min_cost)
    if can_fill is not None and in_max_spread(current_price, can_fill.price, max_spread):
        return can_fill
    elif minimum_fill is not None and in_max_spread(current_price, minimum_fill.price, max_spread) and not dca:
        return minimum_fill
    else:
        return None


# check min balance, max pairs, quote change, market change, trading enabled, blacklist, whitelist, 24h change
# todo add pair specific settings
def handle_possible_buys(possible_buys):
    global trade_history
    for pair in possible_buys:
        if pair_specific_buy_checks(pair, exchange.pairs[pair]['close'], possible_buys[pair], exchange.balance, exchange.pairs[pair]['percentage'], config['min_buy_balance']):
            # amount we'd like to own
            target_amount = possible_buys[pair]
            # difference between target and current owned quantity.
            remaining_amount = target_amount - exchange.pairs[pair]['total']
            # lowest cost trade-able
            min_cost = exchange.pairs[pair]['limits']['cost']['min']
            current_price = exchange.pairs[pair]['close']

            # get orderbook, if time since last orderbook check is too soon, it will return none
            orderbook = exchange.get_depth(pair, 'BUY')
            if orderbook is None:
                continue

            # get viable trade, returns None if none available
            price_info = check_for_viable_trade(current_price, orderbook, remaining_amount, min_cost, config['max_spread'])

            # Check to see if amount remaining to buy is greater than min trade quantity for pair
            if price_info is None or price_info.amount * price_info.average_price < min_cost:
                continue

            # place order
            order = exchange.place_order(pair, 'limit', 'buy', price_info.amount, price_info.price)
            # store order in trade history
            trade_history.append(order)


# temp variable for monitoring
profits = []
def handle_possible_sells(possible_sells):
    global trade_history, profits
    for pair in possible_sells:
        if exchange.pairs[pair]['total'] * exchange.pairs[pair]['amount'] < DUST_VALUE: continue
        # lowest cost trade-able
        min_cost = exchange.pairs[pair]['limits']['cost']['min']
        lowest_sell_price = possible_sells[pair]
        current_price = exchange.pairs[pair]['close']
        orderbook = exchange.get_depth(pair, 'sell')
        if orderbook is None:
            continue
        can_fill, minimum_fill = process_depth(orderbook, exchange.pairs[pair]['total'], min_cost)
        if can_fill is not None and can_fill.price > lowest_sell_price:
            price = can_fill
        elif minimum_fill is not None and minimum_fill.price > lowest_sell_price:
            price = minimum_fill
        else:
            continue
        current_value = exchange.pairs[pair]['total'] * price.average_price
        profits.append((current_value - exchange.pairs[pair]['total_cost']) / exchange.pairs[pair]['total_cost'] * 100)
        order = exchange.place_order(pair, 'limit', 'sell', exchange.pairs[pair]['total'], price.price)
        trade_history.append(order)

def handle_possible_dca_buys(possible_buys):
    global trade_history
    dca_timeout = config['dca_timeout'] * 60
    for pair in possible_buys:
        if exchange.pairs[pair]['total'] * exchange.pairs[pair]['amount'] < DUST_VALUE \
                or time.time() - exchange.pairs[pair]['last_order_time'] < dca_timeout: continue
        
        if pair_specific_buy_checks(pair, exchange.pairs[pair]['close'], possible_buys[pair], exchange.balance,
                                    exchange.pairs[pair]['percentage'], config['dca_min_buy_balance'], True):
            # lowest cost trade-able
            min_cost = exchange.pairs[pair]['limits']['cost']['min']
            current_price = exchange.pairs[pair]['close']

            # get orderbook, if time since last orderbook check is too soon, it will return none
            orderbook = exchange.get_depth(pair, 'BUY')
            if orderbook is None:
                continue

            # get viable trade, returns None if none available
            price_info = check_for_viable_trade(current_price, orderbook, possible_buys[pair], min_cost,
                                                config['max_spread'], True)

            # Check to see if amount remaining to buy is greater than min trade quantity for pair
            if price_info is None or price_info.amount * price_info.average_price < min_cost:
                continue

            order = exchange.place_order(pair, 'limit', 'buy', possible_buys[pair], exchange.pairs[pair]['close'])
            exchange.pairs[pair]['dca_level'] += 1
            trade_history.append(order)


# this is just here temporarily for personal use
def get_percent_change(_pairs):
    df = pd.DataFrame.from_dict(_pairs, orient='index')
    df['current_value'] = df['total'] * df['close']
    df['change'] = (df['current_value'] - df['total_cost']) / df['total_cost'] * 100
    return df['change'].dropna()


if __name__ == '__main__':
    def run():
        while True:
            do_technical_analysis()
            if global_buy_checks():
                possible_buys = get_possible_buys(exchange.pairs, buy_strategies)
                handle_possible_buys(possible_buys)
                possible_dca_buys = get_possible_buys(exchange.pairs, dca_buy_strategies)
                handle_possible_dca_buys(possible_dca_buys)

            possible_sells = get_possible_sells(exchange.pairs, sell_strategies)
            handle_possible_sells(possible_sells)
            time.sleep(1)


    import threading

    threading.Thread(target=run).start()
    print(get_average_market_change(pairs))
