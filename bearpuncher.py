import asyncio
import json
import time
import traceback
from functools import reduce
import datetime

import pandas as pd

from Config import Config
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

DEFAULT_COLUMNS = ['last_order_time', 'symbol', 'avg_price', 'close', 'gain', 'quoteVolume', 'total_cost', 'current_value', 'dca_level', 'total', 'percentage']

# FRIENDLY_HOLDING_COLUMNS =  ['Last Purchase Time', 'Symbol', 'Price', 'Bought Price', '% Change', 'Volume',
#                              'Bought Value', 'Current Value', 'DCA Level', 'Amount', '24h Change']
COLUMN_ALIASES = {'last_order_time': 'Last Purchase Time',
                 'symbol': 'Symbol',
                 'avg_price': 'Bought Price',
                 'close': 'Price',
                 'gain': '% Change',
                 'quoteVolume': 'Volume',
                 'total_cost': 'Bought Value',
                 'current_value': 'Current Value',
                 'dca_level': 'DCA Level',
                 'total': 'Amount',
                 'percentage': '24h Change'
                  }


FRIENDLY_MARKET_COLUMNS =  ['Symbol', 'Price', 'Volume',
                            'Amount', '24h Change']

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
        self.indicators = None
        self.timeframes = None
        self.owned = []

    def initialize_config(self):
        self.config = Config()
        self.config.load_general_settings()
        self.config.load_global_trade_conditions()
        self.indicators = self.config.get_indicators()
        self.timeframes = self.config.timeframes

    def initialize_exchange(self):
        if self.config.general_settings['exchange'].lower() == 'binance' and self.config.general_settings['paper_trading']:
            self.exchange = PaperBinance.PaperBinance('binance',
                                                      self.config.general_settings['market'].upper(),
                                                      self.config.general_settings['starting_balance'],
                                                      {'public': keys.public, 'secret': keys.secret},
                                                      self.timeframes)

            # use USDT in tests to decrease API calls (only ~12 pairs vs 100+)
        elif self.config.general_settings['exchange'].lower() == 'binance':
            self.exchange = Binance.BinanceExchange('binance',
                                                    self.config.general_settings['market'].upper(),
                                                    {'public': keys.public, 'secret': keys.secret},
                                                    self.timeframes)

        else:
            self.exchange = GenericExchange.GenericExchange(self.config.general_settings['exchange'].lower(),
                                                            self.config.general_settings['market'].upper(),
                                                            {'public': keys.public, 'secret': keys.secret},
                                                            self.timeframes)

        #asyncio.get_event_loop().run_until_complete(self.exchange.initialize())
        event_loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.exchange.initialize(), loop=event_loop)

    # return total current value (pairs + balance)
    def get_tcv(self):
        pending = 0
        self.owned = []

        for pair, value in self.exchange.pairs.items():
            if 'total' not in value or 'close' not in value:
                continue

            pending += value['close'] * value['total']

            if value['close'] * value['total'] > 0:
                self.owned.append(pair)

        return pending + self.exchange.balance

    def load_strategies(self):
        # TODO get candle periods and indicators here or in load config
        # instantiate strategies
        buy_strategies = []
        for strategy in self.config.buy_strategies:
            buy_strategies.append(BuyCondition(strategy))

        dca_buy_strategies = []
        for strategy in self.config.dca_buy_strategies:
            dca_buy_strategies.append(DCABuyCondition(strategy))

        sell_strategies = []
        for strategy in self.config.sell_strategies:
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
                try:
                    result = strategy.evaluate(pairs[pair], self.statistics[pair], tcv)

                except Exception as ex:
                    print('exception in get possible buys: {}'.format(traceback.format_exc()))
                    self.exchange.reload_single_candle_history(pair)
                    continue

                if result is not None:
                    if pair not in possible_trades or possible_trades[pair] > result:
                        possible_trades[pair] = result

            return possible_trades

    def get_possible_sells(self, pairs, strategies):
        possible_trades = {}
        for strategy in strategies:
            for pair in pairs:
                # strategy.evaluate(pairs[pair],statistics[pair])
                result = strategy.evaluate(pairs[pair], self.statistics[pair])

                if result is not None:
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
            if self.pair_specific_buy_checks(pair, self.exchange.pairs[pair]['close'], possible_buys[pair], self.exchange.balance, self.exchange.pairs[pair]['percentage'], self.config.global_trade_conditions['min_buy_balance']):
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
                price_info = self.check_for_viable_trade(current_price, orderbook, remaining_amount, min_cost, self.config.global_trade_conditions['max_spread'])
    
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
        dca_timeout = self.config.global_trade_conditions['dca_timeout'] * 60
        for pair in possible_buys:
            # lowest cost trade-able
            min_cost = self.exchange.get_min_cost(pair)

            if (self.exchange.pairs[pair]['total'] * self.exchange.pairs[pair]['close'] < min_cost
                    or time.time() - self.exchange.pairs[pair]['last_order_time'] < dca_timeout):
                continue

            if self.pair_specific_buy_checks(pair, self.exchange.pairs[pair]['close'], possible_buys[pair],
                                             self.exchange.balance, self.exchange.pairs[pair]['percentage'],
                                             self.config.global_trade_conditions['dca_min_buy_balance'], True):

                current_price = self.exchange.pairs[pair]['close']

                # get orderbook, if time since last orderbook check is too soon, it will return none
                orderbook = self.exchange.get_depth(pair, 'BUY')
                if orderbook is None:
                    continue

                # get viable trade, returns None if none available
                price_info = self.check_for_viable_trade(current_price, orderbook, possible_buys[pair], min_cost,
                                                    self.config.global_trade_conditions['max_spread'], True)

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
                  below_max_change(change, self.config.global_trade_conditions['max_change']),
                  above_min_change(change, self.config.global_trade_conditions['min_change']),
                  not is_blacklisted(pair, self.config.global_trade_conditions['blacklist']),
                  is_whitelisted(pair, self.config.global_trade_conditions['whitelist'])
                  ]

        if not dca:
            checks.append(self.exchange.pairs[pair]['total'] < 0.8 * amount)
            checks.append(below_max_pairs(len(self.owned), self.config.global_trade_conditions['max_pairs']))

        return all(checks)

    def global_buy_checks(self):
        check_24h_quote_change = in_range(self.exchange.quote_change_info['24h'],
                                          self.config.global_trade_conditions['market_change']['min_24h_quote_change'],
                                          self.config.global_trade_conditions['market_change']['max_24h_quote_change'])

        check_1h_quote_change = in_range(self.exchange.quote_change_info['1h'],
                                         self.config.global_trade_conditions['market_change']['min_1h_quote_change'],
                                         self.config.global_trade_conditions['market_change']['max_1h_quote_change'])

        check_24h_market_change = in_range(get_average_market_change(self.exchange.pairs),
                                           self.config.global_trade_conditions['market_change']['min_24h_market_change'],
                                           self.config.global_trade_conditions['market_change']['max_24h_market_change'])

        return all([
            check_1h_quote_change,
            check_24h_market_change,
            check_24h_quote_change
        ])

    def do_technical_analysis(self):
        # todo raise error if indicators none
        for pair in self.exchange.pairs:
            try:
                self.statistics[pair] = run_ta(self.exchange.candles[pair], self.indicators)

            except Exception as ex:
                print('err in do ta', pair, ex)
                self.exchange.reload_single_candle_history(pair)
                continue

    def save_trade_history(self):
        fp = 'tradehistory.json'
        with open(fp, 'w') as f:
            json.dump(self.trade_history, f)

    def load_trade_history(self):
        fp = 'tradehistory.json'
        with open(fp, 'r') as f:
            self.trade_history = json.load(f)

    def pairs_to_df(self, basic = True, friendly = False):
        df = pd.DataFrame.from_dict(self.exchange.pairs, orient='index')

        if 'total_cost' in df:
            df['current_value'] = df.close * df.total
            df['gain'] = (df.current_value - df.total_cost) / df.total_cost * 100

        if friendly:
            df = df[DEFAULT_COLUMNS] if basic else df
            df.rename(columns=COLUMN_ALIASES,
                      inplace=True)
            return df

        else:
            return df[DEFAULT_COLUMNS] if basic else df

    def get_pending_value(self):
        df = self.pairs_to_df()

        if 'total_cost' in df:
            return df.total_cost.sum() + self.exchange.balance
        else:
            return 0

    def get_pair(self, symbol):
        return self.exchange.pairs[symbol]

    @staticmethod
    def calc_gains_on_df(df):
        df['total_cost'] = df.bought_price * df.filled
        df['gain'] = df['cost'] - df['total_cost']
        df['percent_gain'] = (df['cost'] - df['total_cost']) / df['total_cost'] * 100

        return df

    def get_daily_profit_data(self):
        df = pd.DataFrame(self.trade_history + [PaperBinance.create_paper_order(0, 0, 'sell', 0, 0, 0)])
        df = self.calc_gains_on_df(df)

        # todo timezones
        df = df.set_index(
            pd.to_datetime(df.timestamp, unit='ms')
        )

        return df.resample('1d').sum()

    def get_pair_profit_data(self):
        df = pd.DataFrame(self.trade_history)
        df = self.calc_gains_on_df(df)

        return df.groupby('symbol').sum()[['total_cost', 'cost', 'amount', 'gain']]

    def get_total_profit(self):
        df = pd.DataFrame(self.trade_history)
        df = df[df.side == 'sell']

        # filled is the amount filled
        df['total_cost'] = df.bought_price * df.filled
        df['gain'] = df['cost'] - df['total_cost']

        return df.gain.sum()

    def get_cumulative_profit(self):
        return self.get_daily_profit_data().cumsum()
    #     (current_value - self.exchange.pairs[pair]['total_cost']) / self.exchange.pairs[pair]['total_cost'] * 100)

# ----
def main():
    global BP_ENGINE

    BP_ENGINE = Bearpuncher()
    BP_ENGINE.initialize_config()
    BP_ENGINE.load_trade_history()
    BP_ENGINE.initialize_exchange()
    BP_ENGINE.load_strategies()

    def run():
        while BP_ENGINE.exchange.balance is None:
            time.sleep(1)
            print('No balance yet...')

        while True:
            try:
                BP_ENGINE.do_technical_analysis()
                
                if BP_ENGINE.global_buy_checks():
                    possible_buys = BP_ENGINE.get_possible_buys(BP_ENGINE.exchange.pairs, BP_ENGINE.buy_strategies)
                    BP_ENGINE.handle_possible_buys(possible_buys)
                    possible_dca_buys = BP_ENGINE.get_possible_buys(BP_ENGINE.exchange.pairs, BP_ENGINE.dca_buy_strategies)
                    BP_ENGINE.handle_possible_dca_buys(possible_dca_buys)

                possible_sells = BP_ENGINE.get_possible_sells(BP_ENGINE.exchange.pairs, BP_ENGINE.sell_strategies)
                BP_ENGINE.handle_possible_sells(possible_sells)
                time.sleep(1)

            except Exception as ex:
                print('err in run: {}'.format(traceback.format_exc()))

            except KeyboardInterrupt:
                print('Exiting Bearpuncher...')
                break

        BP_ENGINE.exchange.stop()

    import threading
    import FlaskApp

    bpthread = threading.Thread(target=run)
    exchangethread = threading.Thread(target=BP_ENGINE.exchange.start)
    guithread = threading.Thread(target=lambda: FlaskApp.app.run('0.0.0.0', 80))

    bpthread.start()
    exchangethread.start()
    guithread.start()

    input("Bearpuncher is now running, press enter to exit > ")

    # app.run(port=8081)
