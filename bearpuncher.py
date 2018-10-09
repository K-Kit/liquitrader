import json
import time
from functools import reduce

import pandas as pd

from exchanges import Binance
from exchanges import GenericExchange
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

class Bearpuncher:
    """
    Needs:
        - self.exchange
        - Config
        - Buy/sell/dca Strategies

    functions:
        - Analyze buy strategies
        - analyze sell strategies
        - analyze dca strategies

        - Handle possible sells
        - Handle buys
        - handle dca buys

        - get active config
        - update config
        - update strategies
    """
    def __init__(self):
        self.exchange = None
        self.statistics = {}
        self.config = None
        self.buy_strategies = None
        self.sell_strategies = None
        self.dca_buy_strategies = None
        self.trade_history = []
        self.indicators = [
       {'name': 'MFI', 'candle_period': 0},
       {'name': 'BBANDS', 'candle_period': 0},
       {'name': 'MFI', 'candle_period': 32},
       {'name': 'MFI', 'candle_period': 30},
       {'name': 'BBANDS', 'candle_period': 14}]

        self.owned = []

    def load_config(self):
        # todo if null raise error
        filename = 'config/config.json'
        with open(filename, 'r') as f:
            self.config = json.load(f)

    # return total current value (pairs + balance)
    def get_tcv(self):
        pending = 0
        global owned
        self.owned = []
        for pair, value in self.exchange.pairs.items():
            if 'total' not in value or 'close' not in value: continue
            pending += value['close'] * value['total']
            if value['close'] * value['total'] > 0:
                self.owned.append(pair)
        return pending + self.exchange.balance

    def get_timeframes(self):
        if self.config is None:
            raise Exception("Config not found, cannot parse timeframes")
        else:
            timeframes = set()
            for conditions in self.config['buy_strategies']:
                pass
            for conditions in self.config['sell_strategies']:
                pass
            for conditions in self.config['dca_buy_strategies']:
                pass
            # temp
            timeframes.add('5m')
            timeframes.add('30m')
            timeframes.add('1h')
            return timeframes

    def initialize_exchange(self):
        if self.config['exchange'].lower() == 'binance' and self.config['paper_trading']:
            self.exchange = PaperBinance.PaperBinance('binance', self.config['market'].upper(), self.config['starting_balance'],
                                                 {'public': keys.public, 'secret': keys.secret}, self.get_timeframes())
            # use USDT in tests to decrease API calls (only ~12 pairs vs 100+)
        elif self.config['exchange'].lower() == 'binance':
            self.exchange = Binance.BinanceExchange('binance', self.config['market'].upper(),
                                                 {'public': keys.public, 'secret': keys.secret}, self.get_timeframes())
        else:
            self.exchange = GenericExchange.GenericExchange(self.config['exchange'].lower(), self.config['market'].upper(),
                                                 {'public': keys.public, 'secret': keys.secret}, self.get_timeframes())
        self.exchange.initialize()

    def load_strategies(self):
        # TODO get candle periods and indicators here or in load config
        # instantiate strategies
        buy_strategies = []
        for strategy in self.config['buy_strategies']:
            buy_strategies.append(BuyCondition(strategy))

        dca_buy_strategies = []
        for strategy in self.config['dca_buy_strategies']:
            dca_buy_strategies.append(DCABuyCondition(strategy))

        sell_strategies = []
        for strategy in self.config['sell_strategies']:
            sell_strategies.append(SellCondition(strategy))

        self.buy_strategies = buy_strategies
        self.sell_strategies = sell_strategies
        self.dca_buy_strategies = dca_buy_strategies

    def get_possible_buys(self, pairs, strategies):
        possible_trades = {}
        tcv = self.get_tcv()
        for strategy in strategies:
            for pair in pairs:
                # strategy.evaluate(pairs[pair],statistics[pair])
                result = strategy.evaluate(pairs[pair], self.statistics[pair], tcv)
                if not result is None:
                    if pair not in possible_trades or possible_trades[pair] > result:
                        possible_trades[pair] = result
            return possible_trades

    def get_possible_sells(self, pairs, strategies):
        possible_trades = {}
        for strategy in strategies:
            for pair in pairs:
                # strategy.evaluate(pairs[pair],statistics[pair])
                result = strategy.evaluate(pairs[pair], self.statistics[pair])
                if not result is None:
                    if pair not in possible_trades or possible_trades[pair] < result:
                        possible_trades[pair] = result
            return possible_trades

    @staticmethod
    def check_for_viable_trade(current_price, orderbook, remaining_amount, min_cost, max_spread, dca=False):
        can_fill, minimum_fill = process_depth(orderbook, remaining_amount, min_cost)
        if can_fill is not None and in_max_spread(current_price, can_fill.price, max_spread):
            return can_fill
        elif minimum_fill is not None and in_max_spread(current_price, minimum_fill.price, max_spread) and not dca:
            return minimum_fill
        else:
            return None

    # check min balance, max pairs, quote change, market change, trading enabled, blacklist, whitelist, 24h change
    # todo add pair specific settings
    def handle_possible_buys(self, possible_buys):
        for pair in possible_buys:
            if self.pair_specific_buy_checks(pair, self.exchange.pairs[pair]['close'], possible_buys[pair], self.exchange.balance, self.exchange.pairs[pair]['percentage'], self.config['min_buy_balance']):
                # amount we'd like to own
                target_amount = possible_buys[pair]
                # difference between target and current owned quantity.
                remaining_amount = target_amount - self.exchange.pairs[pair]['total']
                # lowest cost trade-able
                min_cost = self.exchange.get_min_cost(pair)
                current_price = self.exchange.pairs[pair]['close']
    
                # get orderbook, if time since last orderbook check is too soon, it will return none
                orderbook = self.exchange.get_depth(pair, 'BUY')
                if orderbook is None:
                    continue
    
                # get viable trade, returns None if none available
                price_info = self.check_for_viable_trade(current_price, orderbook, remaining_amount, min_cost, self.config['max_spread'])
    
                # Check to see if amount remaining to buy is greater than min trade quantity for pair
                if price_info is None or price_info.amount * price_info.average_price < min_cost:
                    continue
    
                # place order
                order = self.exchange.place_order(pair, 'limit', 'buy', price_info.amount, price_info.price)
                # store order in trade history
                self.trade_history.append(order)
                self.save_trade_history()

    def handle_possible_sells(self, possible_sells):
        for pair in possible_sells:
            
            # lowest cost trade-able
            min_cost = self.exchange.get_min_cost(pair)
            if self.exchange.pairs[pair]['total'] * self.exchange.pairs[pair]['close'] < min_cost: continue
            
            lowest_sell_price = possible_sells[pair]
            current_price = self.exchange.pairs[pair]['close']
            orderbook = self.exchange.get_depth(pair, 'sell')
            if orderbook is None:
                continue
            can_fill, minimum_fill = process_depth(orderbook, self.exchange.pairs[pair]['total'], min_cost)
            if can_fill is not None and can_fill.price > lowest_sell_price:
                price = can_fill
            elif minimum_fill is not None and minimum_fill.price > lowest_sell_price:
                price = minimum_fill
            else:
                continue
            current_value = self.exchange.pairs[pair]['total'] * price.average_price
            # profits.append(
            #     (current_value - self.exchange.pairs[pair]['total_cost']) / self.exchange.pairs[pair]['total_cost'] * 100)
            order = self.exchange.place_order(pair, 'limit', 'sell', self.exchange.pairs[pair]['total'], price.price)
            self.trade_history.append(order)
            self.save_trade_history()

    def handle_possible_dca_buys(self, possible_buys):
        dca_timeout = self.config['dca_timeout'] * 60
        for pair in possible_buys:
            min_cost = self.exchange.get_min_cost(pair)
            if self.exchange.pairs[pair]['total'] * self.exchange.pairs[pair]['amount'] < min_cost \
                    or time.time() - self.exchange.pairs[pair]['last_order_time'] < dca_timeout: continue

            if self.pair_specific_buy_checks(pair, self.exchange.pairs[pair]['close'], possible_buys[pair], self.exchange.balance,
                                        self.exchange.pairs[pair]['percentage'], self.config['dca_min_buy_balance'], True):
                # lowest cost trade-able
                
                current_price = self.exchange.pairs[pair]['close']

                # get orderbook, if time since last orderbook check is too soon, it will return none
                orderbook = self.exchange.get_depth(pair, 'BUY')
                if orderbook is None:
                    continue

                # get viable trade, returns None if none available
                price_info = self.check_for_viable_trade(current_price, orderbook, possible_buys[pair], min_cost,
                                                    self.config['max_spread'], True)

                # Check to see if amount remaining to buy is greater than min trade quantity for pair
                if price_info is None or price_info.amount * price_info.average_price < min_cost:
                    continue

                order = self.exchange.place_order(pair, 'limit', 'buy', possible_buys[pair], self.exchange.pairs[pair]['close'])
                self.exchange.pairs[pair]['dca_level'] += 1
                self.trade_history.append(order)
                self.save_trade_history()

    def pair_specific_buy_checks(self, pair, price, amount, balance, change, min_balance, dca=False):
        min_balance = min_balance if not isinstance(min_balance, str) \
            else percentToFloat(min_balance) * self.get_tcv()
        checks = [not exceeds_min_balance(balance, min_balance, price, amount),
                  below_max_change(change, self.config['max_change']),
                  above_min_change(change, self.config['min_change']),
                  not is_blacklisted(pair, self.config['blacklist']),
                  is_whitelisted(pair, self.config['whitelist'])
                  ]
        if not dca:
            checks.append(self.exchange.pairs[pair]['total'] < 0.8 * amount)
            checks.append(below_max_pairs(len(self.owned), self.config['max_pairs']))
        return all(checks)

    def global_buy_checks(self):
        check_24h_quote_change = in_range(self.exchange.quote_change_info['24h'],
                                          self.config['market_change']['min_24h_quote_change'],
                                          self.config['market_change']['max_24h_quote_change'])

        check_1h_quote_change = in_range(self.exchange.quote_change_info['1h'],
                                         self.config['market_change']['min_1h_quote_change'],
                                         self.config['market_change']['max_1h_quote_change'])

        check_24h_market_change = in_range(get_average_market_change(self.exchange.pairs),
                                           self.config['market_change']['min_24h_market_change'],
                                           self.config['market_change']['max_24h_market_change'])

        return all([
            check_1h_quote_change,
            check_24h_market_change,
            check_24h_quote_change
        ])

    def do_technical_analysis(self):
        # todo raise error if indicators none
        for pair in self.exchange.pairs:
            self.statistics[pair] = run_ta(self.exchange.candles[pair], self.indicators)

    def save_trade_history(self):
        fp = 'tradehistory.json'
        with open(fp, 'w') as f:
            json.dump(self.trade_history, f)


    def load_trade_history(self):
        fp = 'tradehistory.json'
        with open(fp, 'r') as f:
            self.trade_history = json.load(f)



if __name__ == '__main__':

    def get_trades_frame():
        df = pd.DataFrame(bp.trade_history)
        df['gain'] = (df.price - df.bought_price) / df.bought_price * 100
        cols = ['symbol', 'bought_price', 'price', 'amount', 'side', 'status', 'remaining', 'filled', 'gain']
        return df[cols]

    def get_relevent_pair_data(additional_columns = None):
        return pd.DataFrame.from_dict(bp.exchange.pairs, orient='index')

    bp = Bearpuncher()
    bp.load_config()
    bp.load_trade_history()
    bp.get_timeframes()
    bp.initialize_exchange()
    bp.load_strategies()

    def run():
        while True:
            bp.do_technical_analysis()
            if bp.global_buy_checks():
                possible_buys = bp.get_possible_buys(bp.exchange.pairs, bp.buy_strategies)
                bp.handle_possible_buys(possible_buys)
                possible_dca_buys = bp.get_possible_buys(bp.exchange.pairs, bp.dca_buy_strategies)
                bp.handle_possible_dca_buys(possible_dca_buys)

            possible_sells = bp.get_possible_sells(bp.exchange.pairs, bp.sell_strategies)
            bp.handle_possible_sells(possible_sells)
            time.sleep(1)


    import threading

    thread = threading.Thread(target=run)
    thread2 = threading.Thread(target=bp.exchange.start)
    thread.start()
    thread2.start()
