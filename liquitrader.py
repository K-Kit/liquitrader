import asyncio
import os
import sys
import json
import time
import traceback
import threading
import functools
import pathlib

import arrow


from config.config import Config
from exchanges import BinanceExchange
from exchanges import GenericExchange
from exchanges import GenericPaper
from utils.DepthAnalyzer import *

from exchanges import PaperBinance
from analyzers.TechnicalAnalysis import run_ta
from conditions.BuyCondition import BuyCondition
from conditions.DCABuyCondition import DCABuyCondition
from conditions.SellCondition import SellCondition
from utils.Utils import *
from conditions.condition_tools import get_buy_value


from conditions.condition_tools import percentToFloat
from utils.FormattingTools import prettify_dataframe

import getpass

LT_ENGINE = None

APP_DIR = ''
if hasattr(sys, 'frozen'):
    APP_DIR = pathlib.Path(os.path.dirname(sys.executable))
    os.chdir(APP_DIR)
    os.environ["REQUESTS_CA_BUNDLE"] = str(APP_DIR / 'lib' / 'cacert.pem')

else:
    APP_DIR = pathlib.Path(os.path.dirname(__file__))

DEFAULT_COLUMNS = ['last_order_time', 'symbol', 'avg_price', 'close', 'gain', 'quoteVolume', 'total_cost',
                   'current_value', 'dca_level', 'total', 'percentage']

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

FRIENDLY_MARKET_COLUMNS = ['Symbol', 'Price', 'Volume',
                           'Amount', '24h Change']


# =============================
class ShutdownHandler:

    def __init__(self):
        self._counter = 0
        self._shutdown_in_progress = threading.Event()

    def add_task(self):
        self._counter += 1

    def remove_task(self):
        self._counter -= 1

    def start_shutdown(self):
        self._shutdown_in_progress.set()

    def is_complete(self):
        return self._counter == 0

    def running_or_complete(self):
        return self._shutdown_in_progress.is_set() or self.is_complete()

    def nop_on_shutdown(self, func):
        @functools.wraps(func)
        def nopper(*args, **kwargs):
            return None if self.running_or_complete() else func(*args, **kwargs)

        return nopper


class LiquiTrader:
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

    def __init__(self, shutdown_handler):
        self.shutdown_handler = shutdown_handler
        self.market_change_24h = 0
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
        self.possible_trades = []
        self.below_max_pairs = False

    # ----
    def initialize_config(self):
        self.config = Config(self.update_config)
        self.config.load_general_settings()
        self.config.load_global_trade_conditions()
        self.config.load_pair_settings()
        self.indicators = self.config.get_indicators()
        self.timeframes = self.config.timeframes

    # ----
    def update_config(self, strategies=False):
        old_timeframes = self.timeframes
        self.config.load_general_settings()
        self.config.load_global_trade_conditions()
        self.config.load_pair_settings()
        self.timeframes = self.config.timeframes
        self.load_strategies()
        self.indicators = self.config.get_indicators()
        #todo fix and make more efficient, currently always updating
        timeframes_changed = False
        for tf in self.config.timeframes:
            if tf not in old_timeframes:
                timeframes_changed = True
        if timeframes_changed:
            print("timeframe_changed")
            self.exchange.reload_candles()

    # ----
    def initialize_exchange(self):
        general_settings = self.config.general_settings
        general_settings['starting_balance'] = float(general_settings['starting_balance'])
        from gui.gui_server import get_keys
        keys = get_keys()
        if general_settings['exchange'].lower() == 'binance' and general_settings['paper_trading']:
            self.exchange = PaperBinance.PaperBinance('binance',
                                                      general_settings['market'].upper(),
                                                      general_settings['starting_balance'],
                                                      keys,
                                                      self.timeframes)

        # use USDT in tests to decrease API calls (only ~12 pairs vs 100+)
        elif general_settings['exchange'].lower() == 'binance':
            self.exchange = BinanceExchange.BinanceExchange('binance',
                                                            general_settings['market'].upper(),
                                                            general_settings['starting_balance'],
                                                            keys,
                                                            self.timeframes)

        elif general_settings['paper_trading']:
            self.exchange = GenericPaper.PaperGeneric(general_settings['exchange'].lower(),
                                                      general_settings['market'].upper(),
                                                      general_settings['starting_balance'],
                                                      keys,
                                                      self.timeframes)
        else:
            self.exchange = GenericExchange.GenericExchange(general_settings['exchange'].lower(),
                                                            general_settings['market'].upper(),
                                                            general_settings['starting_balance'],
                                                            keys,
                                                            self.timeframes)

        asyncio.get_event_loop().run_until_complete(self.exchange.initialize())

    # ----
    def run_exchange(self):
        import utils.runtime_handler
        utils.runtime_handler.enable_traceback_hook()  # Enable custom traceback handling (to strip build path info)

        self.shutdown_handler.add_task()

        try:
            self.exchange.start()

        # Catch Twisted connection lost bullshit
        except Exception as _ex:
            exception_data = traceback.format_exc()
            if 'connectionLost' in exception_data:
                pass
            else:
                raise _ex

    # ----
    def stop_exchange(self):
        self.exchange.stop()
        self.shutdown_handler.remove_task()

    # ----
    # return total current value (pairs + balance)
    def get_tcv(self):
        pending = 0
        self.owned = []

        for pair, value in self.exchange.pairs.items():
            if 'total' not in value or 'close' not in value:
                continue

            pending += value['close'] * value['total']

            if value['close'] * value['total'] > self.exchange.get_min_cost(pair):
                self.owned.append(pair)
            else:
                self.exchange.pairs[pair]['dca_level'] = 0

        return pending + self.exchange.balance

    # ----
    def load_strategies(self):
        # TODO get candle periods and indicators here or in load config
        # instantiate strategies
        buy_strategies = []
        for strategy in self.config.buy_strategies:
            buy_strategies.append(BuyCondition(strategy, pair_settings=self.config.pair_specific_settings))

        dca_buy_strategies = []
        for strategy in self.config.dca_buy_strategies:
            dca_buy_strategies.append(DCABuyCondition(strategy, pair_settings=self.config.pair_specific_settings))

        sell_strategies = []
        for strategy in self.config.sell_strategies:
            sell_strategies.append(SellCondition(strategy, pair_settings=self.config.pair_specific_settings))

        self.buy_strategies = buy_strategies
        self.sell_strategies = sell_strategies
        self.dca_buy_strategies = dca_buy_strategies

    # ----
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
        self.possible_trades = possible_trades
        return possible_trades

    # ----
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

    # ----
    @staticmethod
    def check_for_viable_trade(current_price, orderbook, remaining_amount, min_cost, max_spread, dca=False):
        can_fill, minimum_fill = process_depth(orderbook, remaining_amount, min_cost)

        if can_fill is not None and in_max_spread(current_price, can_fill.price, max_spread):
            return can_fill

        elif minimum_fill is not None and in_max_spread(current_price, minimum_fill.price, max_spread) and not dca:
            return minimum_fill

        else:
            return None

    # ----
    # check min balance, max pairs, quote change, market change, trading enabled, blacklist, whitelist, 24h change
    # todo add pair specific settings
    def handle_possible_buys(self, possible_buys):
        # Alleviate lookup cost
        exchange = self.exchange
        config = self.config
        exchange_pairs = exchange.pairs

        for pair in possible_buys:
            exch_pair = exchange_pairs[pair]

            if self.pair_specific_buy_checks(pair, exch_pair['close'], possible_buys[pair],
                                             exchange.balance, exch_pair['percentage'],
                                             config.global_trade_conditions['min_buy_balance']):

                # amount we'd like to own
                target_amount = possible_buys[pair]
                # difference between target and current owned quantity.
                remaining_amount = target_amount - exch_pair['total']
                # lowest cost trade-able
                min_cost = exchange.get_min_cost(pair)
                current_price = exch_pair['close']

                # get orderbook, if time since last orderbook check is too soon, it will return none
                orderbook = exchange.get_depth(pair, 'BUY')
                if orderbook is None:
                    continue

                # get viable trade, returns None if none available
                price_info = self.check_for_viable_trade(current_price, orderbook, remaining_amount, min_cost,
                                                         config.global_trade_conditions['max_spread'])

                # Check to see if amount remaining to buy is greater than min trade quantity for pair
                if price_info is None or price_info.amount * price_info.average_price < min_cost:
                    continue

                # place order
                order = exchange.place_order(pair, 'limit', 'buy', price_info.amount, price_info.price)
                # store order in trade history
                self.trade_history.append(order)
                self.save_trade_history()

    # ----
    def handle_possible_sells(self, possible_sells):
        # Alleviate lookup cost
        exchange = self.exchange
        exchange_pairs = exchange.pairs

        for pair in possible_sells:
            exch_pair = exchange_pairs[pair]

            # lowest cost trade-able
            min_cost = exchange.get_min_cost(pair)
            if exch_pair['total'] * exch_pair['close'] < min_cost:
                continue

            orderbook = exchange.get_depth(pair, 'sell')
            if orderbook is None:
                continue

            lowest_sell_price = possible_sells[pair]

            can_fill, minimum_fill = process_depth(orderbook, exch_pair['total'], min_cost)
            if can_fill is not None and can_fill.price > lowest_sell_price:
                price = can_fill

            elif minimum_fill is not None and minimum_fill.price > lowest_sell_price:
                price = minimum_fill

            else:
                continue

            current_value = exch_pair['total'] * price.average_price

            order = exchange.place_order(pair, 'limit', 'sell', exch_pair['total'], price.price)
            self.trade_history.append(order)
            self.save_trade_history()

    # ----
    def handle_possible_dca_buys(self, possible_buys):
        # Alleviate lookup cost
        exchange = self.exchange
        config = self.config
        exchange_pairs = exchange.pairs
        
        dca_timeout = float(config.global_trade_conditions['dca_timeout']) * 60
        for pair in possible_buys:
            exch_pair = exchange_pairs[pair]

            # lowest cost trade-able
            min_cost = exchange.get_min_cost(pair)

            if (exch_pair['total'] * exch_pair['close'] < min_cost
                    or time.time() - exch_pair['last_order_time'] < dca_timeout):
                continue

            if self.pair_specific_buy_checks(pair, exch_pair['close'], possible_buys[pair],
                                             exchange.balance, exch_pair['percentage'],
                                             config.global_trade_conditions['dca_min_buy_balance'], True):

                current_price = exch_pair['close']

                # get orderbook, if time since last orderbook check is too soon, it will return none
                orderbook = exchange.get_depth(pair, 'BUY')
                if orderbook is None:
                    continue

                # get viable trade, returns None if none available
                price_info = self.check_for_viable_trade(current_price, orderbook, possible_buys[pair], min_cost,
                                                         config.global_trade_conditions['max_spread'], True)

                # Check to see if amount remaining to buy is greater than min trade quantity for pair
                if price_info is None or price_info.amount * price_info.average_price < min_cost:
                    continue

                order = exchange.place_order(pair, 'limit', 'buy', possible_buys[pair], exch_pair['close'])
                if order['cost'] > min_cost:
                    exch_pair['dca_level'] += 1
                self.trade_history.append(order)
                self.save_trade_history()

    # ----
    def pair_specific_buy_checks(self, pair, price, amount, balance, change, min_balance, dca=False):
        # Alleviate lookup cost
        global_trade_conditions = self.config.global_trade_conditions

        min_balance = min_balance if not isinstance(min_balance, str) \
            else percentToFloat(min_balance) * self.get_tcv()
        self.below_max_pairs = self.is_below_max_pairs(len(self.owned), int(global_trade_conditions['max_pairs']))
        checks = [not exceeds_min_balance(balance, min_balance, price, amount),
                  below_max_change(change, global_trade_conditions['max_change']),
                  above_min_change(change, global_trade_conditions['min_change']),
                  not is_blacklisted(pair, global_trade_conditions['blacklist']),
                  is_whitelisted(pair, global_trade_conditions['whitelist'])
                  ]

        if not dca:
            checks.append(self.exchange.pairs[pair]['total'] < 0.8 * amount)
            checks.append(self.below_max_pairs)
        return all(checks)

    @staticmethod
    def is_below_max_pairs(current_pairs, max_pairs):
        return current_pairs < max_pairs or max_pairs == 0

    # ----
    def global_buy_checks(self):
        # Alleviate lookup cost
        quote_change_info = self.exchange.quote_change_info
        market_change = self.config.global_trade_conditions
        self.market_change_24h = get_average_market_change(self.exchange.pairs)
        self.below_max_pairs = self.is_below_max_pairs(len(self.owned),
                                                       int(self.config.global_trade_conditions['max_pairs']))
        self.check_24h_quote_change = in_range(quote_change_info['24h'],
                                               market_change['min_24h_quote_change'],
                                               market_change['max_24h_quote_change'])

        self.check_1h_quote_change = in_range(quote_change_info['1h'],
                                              market_change['min_1h_quote_change'],
                                              market_change['max_1h_quote_change'])

        self.check_24h_market_change = in_range(self.market_change_24h,
                                                market_change['min_24h_market_change'],
                                                market_change['max_24h_market_change'])

        return all((
            self.check_1h_quote_change,
            self.check_24h_market_change,
            self.check_24h_quote_change
        ))

    # ----
    def do_technical_analysis(self):
        candles = self.exchange.candles

        for pair in self.exchange.pairs:
            if self.indicators is None:
                raise TypeError('(do_technical_analysis) LiquiTrader.indicators cannot be None')

            try:
                self.statistics[pair] = run_ta(candles[pair], self.indicators)

            except Exception as ex:
                print('err in do ta', pair, ex)
                self.exchange.reload_single_candle_history(pair)
                continue

    # ----
    def save_trade_history(self):
        self.save_pairs_history()
        fp = 'tradehistory.json'
        with open(fp, 'w') as f:
            json.dump(self.trade_history, f)

    # ----
    def save_pairs_history(self):
        self.exchange.save()

    # ----
    def load_pairs_history(self):
        fp = 'pair_data.json'

        with open(fp, 'r') as f:
            pair_data = json.load(f)

        exchange_pairs = self.exchange.pairs
        for pair in exchange_pairs:
            if pair in pair_data:
                exch_pair = exchange_pairs[pair]

                # TODO @Kyle :: was the 'or' removed?
                if exch_pair['total_cost'] is None or self.config.general_settings['paper_trading']:
                    exch_pair.update(pair_data[pair])
                else:
                    exch_pair['dca_level'] = pair_data[pair]['dca_level']
                    exch_pair['last_order_time'] = pair_data[pair]['last_order_time']

    # ----
    def load_trade_history(self):
        fp = 'tradehistory.json'
        with open(fp, 'r') as f:
            self.trade_history = json.load(f)

    def pairs_to_df(self, basic=True, friendly=False, holding=False, fee=0.075):
        df = pd.DataFrame.from_dict(self.exchange.pairs, orient='index')
        times = []

        timezone = self.config.general_settings['timezone']
        try:
            arrow.utcnow().to(timezone)  # Try to parse timezone

        except arrow.parser.ParserError:
            print('Invalid timezone in config, defaulting to UTC')
            timezone = 'UTC'

        for t in df.last_order_time.values:
            times.append(arrow.get(t).to(timezone).datetime)

        df.last_order_time = pd.DatetimeIndex(times)

        if 'total_cost' in df and 'close' in df:
            df['current_value'] = df.close * df.total * (1 - (fee / 100))
            df['gain'] = (df.bid - df.avg_price) / df.avg_price * 100 - fee
            if holding:
                dust = 0.02 if self.config.general_settings['market'].upper() == 'ETH' else 0.002
                df = df[df.total_cost > dust]

        if friendly:
            try:
                if len(df) > 0:
                    df = prettify_dataframe(df, self.exchange.quote_price)

            except ValueError as ex:
                pass

            except TypeError as ex:
                pass
            try:
                df = df[DEFAULT_COLUMNS] if basic else df
            except KeyError as ex:
                pass
            df.rename(columns=COLUMN_ALIASES,
                      inplace=True)
            return df

        else:
            return df

    # ----
    def get_pending_value(self):
        df = self.pairs_to_df()

        if 'total_cost' in df:
            return df.total_cost.sum() + self.exchange.balance
        else:
            return 0

    # ----
    def get_pair(self, symbol):
        return self.exchange.pairs[symbol]

    # ----
    @staticmethod
    def calc_gains_on_df(df):
        if 'bought_price' in df:
            df['total_cost'] = df.bought_price * df.filled
            df['gain'] = df['cost'] - df['total_cost']
            df['percent_gain'] = (df['cost'] - df['total_cost']) / df['total_cost'] * 100
            return df

        else:
            df['total_cost'] = 0
            df['gain'] = 0
            df['percent_gain'] = 0
            return df

    # ----
    def get_daily_profit_data(self):
        if len(self.trade_history) < 1:
            df = pd.DataFrame(self.trade_history + [PaperBinance.create_paper_order(0, 0, 'sell', 0, 0, 0)])
        else:
            df = pd.DataFrame(self.trade_history)
        df = self.calc_gains_on_df(df[df.side == 'sell'])

        times = []
        # todo timezones
        df = df.set_index(
            pd.to_datetime(df.timestamp, unit='ms')
        )
        for t in df.timestamp.values:
            times.append(arrow.get(t / 1000).to(self.config.general_settings['timezone']).datetime)

        df.timestamp = pd.DatetimeIndex(times)
        df.index = pd.DatetimeIndex(times)
        df = df.resample('1d').sum()
        df['date'] = df.index
        return df

    # ----
    def get_pair_profit_data(self):
        df = pd.DataFrame(self.trade_history)

        df = self.calc_gains_on_df(df)

        if len(df) == 0 or 'symbol' not in df:
            return df

        return df.groupby('symbol').sum()[['total_cost', 'cost', 'amount', 'gain']]

    # ----
    def get_total_profit(self):
        df = pd.DataFrame(self.trade_history)

        if 'side' not in df:
            return 0

        df = df[df.side == 'sell']

        if len(df) == 0:
            return 0
        # filled is the amount filled
        df['total_cost'] = df.bought_price * df.filled
        df['gain'] = df['cost'] - df['total_cost']

        return df.gain.sum()

    # ----
    def get_cumulative_profit(self):
        df = self.get_daily_profit_data().drop(['date'], axis=1).cumsum()
        df['date'] = df.index
        return df

    # ----
    def get_trailing_pairs(self):
        return {
            "buy": list(map(vars,
                        self.buy_strategies)),

            "sell": list(map(vars,
                        self.sell_strategies)),

            "dca": list(map(vars,
                        self.dca_buy_strategies))
        }


def print_line(text=''):
    sys.stdout.write(text + '\n')

def get_password():
    while True:
        password = input('Password: ')
        confirm = input('Confirm: ')

        if password == '':
            print_line('Password cannot be empty')
        elif password == confirm:
            break
        else:
            print_line('Passwords did not match\n')

    return password


def get_username():
    while 1:
        username = input('Username: ')

        if username != '':
            break
        else:
            print_line('Username cannot be empty')

    return username




# ----
def trader_thread_loop(lt_engine, _shutdown_handler):
    import utils.runtime_handler
    utils.runtime_handler.enable_traceback_hook()  # Enable custom traceback handling (to strip build path info)

    _shutdown_handler.add_task()

    # Alleviate method lookup overhead
    global_buy_checks = lt_engine.global_buy_checks
    do_technical_analysis = lt_engine.do_technical_analysis
    get_possible_buys = lt_engine.get_possible_buys
    handle_possible_buys = lt_engine.handle_possible_buys
    handle_possible_dca_buys = lt_engine.handle_possible_dca_buys
    get_possible_sells = lt_engine.get_possible_sells
    handle_possible_sells = lt_engine.handle_possible_sells

    exchange = lt_engine.exchange
    config = lt_engine.config
    i = 0
    while not _shutdown_handler.running_or_complete():
        try:
            # timed @ 1.1 seconds 128ms stdev
            # only run once per minute, any more than that is not necessary
            if i % 200 == 0:
                do_technical_analysis()
            i += 1

            from pprint import pprint
            # pprint(exchange.pairs)

            possible_buys = get_possible_buys(exchange.pairs, lt_engine.buy_strategies)
            possible_dca_buys = get_possible_buys(exchange.pairs, lt_engine.dca_buy_strategies)
            if global_buy_checks() and config.general_settings['trading_enabled'] and not config.general_settings['sell_only_mode']:
                    handle_possible_buys(possible_buys)
                    handle_possible_dca_buys(possible_dca_buys)
            possible_sells = get_possible_sells(exchange.pairs, lt_engine.sell_strategies)
            # Don't make sells if not trading enabled
            if config.general_settings['trading_enabled']:
                handle_possible_sells(possible_sells)


        except Exception as ex:
            print('err in run: {}'.format(traceback.format_exc()))

    _shutdown_handler.remove_task()

def firsttime_init(shutdown_handler):
    """
    Create user account on first run
    """

    print_line("\n###########################################")
    if input('Do you agree to the LiquiTrader terms of service as found in TOS.txt? (y/n): ') == 'n':
        print_line('\nWe\'re sorry to hear that. Agreeing to the ToS is mandatory, so we\'ll have to call it quits.')
        print_line('Have a great day!\n')
        sys.exit(0)

    print_line('\nFirst time configuration\n')
    # get port and host ip to init gserver
    port = input('Select a port (default: 7007): ')
    if port is None or port =='':
        port = 7007
    else:
        port = int(port)

    host = input('Select a host IP (default: 0.0.0.0 this will expose your machine to the internet, 127.0.0.1 to run locally): ')
    if host is None or host == '':
        host = '0.0.0.0'

    import gui.gui_server
    gui_server = gui.gui_server.GUIServer(shutdown_handler,
                                          host=host,
                                          port=port,
                                          )
    gui_thread = threading.Thread(target=gui_server.run)
    gui_thread.start()
    while not gui.gui_server.users_exist():
        time.sleep(1)
    print("Restarting web server and getting LiquiTrader ready for action.")
    gui_server.stop()
    return


# ----
def main(ipython=False):
    import gui.gui_server

    def err_msg():
        sys.stdout.write('LiquiTrader has been illegitimately modified and must be reinstalled.\n')
        sys.stdout.write(
            'We recommend downloading it manually from our website in case your updater has been compromised.\n\n')
        sys.stdout.flush()

    print('Starting LiquiTrader...\n')

    if 'python' not in sys.executable.lower():
        setattr(sys, 'frozen', True)

    # ----
    shutdown_handler = ShutdownHandler()

    lt_engine = LiquiTrader(shutdown_handler)
    if not gui.gui_server.users_exist():
        firsttime_init(shutdown_handler)

    # todo rewrite first time init
    # take port as input in terminal
    # write port to general settings
    # start server  and reroute to '/setup'
    # write '/first_run' endpoint which takes in a list of steps to init user and write config files
    # list order: account info, general settings, global trade, buy strats, sell strats, dca strats, pair_specific
    try:
        lt_engine.initialize_config()
    except FileNotFoundError:
        firsttime_init(shutdown_handler)
        time.sleep(1)
        lt_engine.initialize_config()

    gui.gui_server.LT_ENGINE = lt_engine

    # get config from lt
    config = lt_engine.config

    # ---- moved this because it cant happen before first run
    if hasattr(sys, 'frozen') or not (os.path.isfile('requirements-win.txt') and os.path.isfile('.gitignore')):
        import analyzers.strategic_analysis as strategic_analysis
        # Check that verifier string hasn't been modified, it exists, and it is a reasonable size
        # If "LiquiTrader has been illegitimately..." is thrown when it shouldn't, check strategic_analysis file size
        if sys.platform == 'win32':
            if ((not os.path.isfile('lib/analyzers.strategic_analysis.pyd'))
                    or os.stat('lib/analyzers.strategic_analysis.pyd').st_size < 268000):
                err_msg()
                sys.exit(1)

        else:
            if ((not os.path.isfile('lib/analyzers.strategic_analysis.so'))
                    or os.stat('lib/analyzers.strategic_analysis.so').st_size < 760000):
                err_msg()
                sys.exit(1)

        time.perf_counter()
        strategic_analysis.verify()

        # Check that verifier took a reasonable amount of time to execute (prevent simple NOPing)
        if time.perf_counter() < .01:
            err_msg()
            sys.exit(1)

        # ----
        # TODO: GET LICENSE KEY AND PUBLIC API KEY FROM CONFIG HERE
        from analyzers import strategic_tools
        from gui.gui_server import get_keys
        keys = get_keys()
        license_key = keys['liquitrader_key']
        api_key = keys['public']

        start = time.perf_counter()
        strategic_tools.verify(license_key, api_key)

        if (time.perf_counter() - start) < .01:
            print('Verification error (A plea from the devs: we\'ve poured our souls into LiquiTrader;'
                  'please stop trying to crack our license system. This is how we keep food on our tables.)')
            sys.exit(1)

    # ----
    shutdown_handler = ShutdownHandler()

    lt_engine = LiquiTrader(shutdown_handler)
    # todo rewrite first time init
    # take port as input in terminal
    # write port to general settings
    # start server  and reroute to '/setup'
    # write '/first_run' endpoint which takes in a list of steps to init user and write config files
    # list order: account info, general settings, global trade, buy strats, sell strats, dca strats, pair_specific
    try:
        lt_engine.initialize_config()
    except FileNotFoundError:
        firsttime_init(shutdown_handler)
        time.sleep(1)
        lt_engine.initialize_config()

    # ----

    gui.gui_server.LT_ENGINE = lt_engine

    # get config from lt
    config = lt_engine.config
    if not gui.gui_server.users_exist():
        firsttime_init(shutdown_handler)

    gui_server = gui.gui_server.GUIServer(shutdown_handler,
                                          host=config.general_settings['host'],
                                          port=config.general_settings['port'],
                                          ssl=config.general_settings['use_ssl'],
                                          )



    try:
        lt_engine.load_trade_history()
    except FileNotFoundError:
        print('No trade history found')

    lt_engine.initialize_exchange()
    lt_engine.load_strategies()

    # ----
    trader_thread = threading.Thread(target=lambda: trader_thread_loop(lt_engine, shutdown_handler))
    gui_thread = threading.Thread(target=gui_server.run)
    exchange_thread = threading.Thread(target=lt_engine.run_exchange)

    trader_thread.start()
    gui_thread.start()
    exchange_thread.start()

    def shutdown():
        print('\nClosing LiquiTrader...\n')

        shutdown_handler.start_shutdown()  # Set shutdown flag

        print('Stopping GUI server')
        gui_server.stop()  # Gracefully shut down webserver

        print('Stopping exchange connections')
        try:
            lt_engine.stop_exchange()

        # Catch Twisted connection lost bullshit
        except Exception:
            exception_data = traceback.format_exc()

            if 'connectionLost' in exception_data:
                pass

            else:
                sys.stdout.write(str(exception_data) + '\n')
                sys.stdout.flush()

        # Wait for transactions / critical actions to finish
        if not shutdown_handler.is_complete():
            counter = 1

            while counter <= 10 and (not shutdown_handler.is_complete()):
                print(f'\rWaiting for transactions to complete... ({counter}/10)...', end='')
                time.sleep(1)
                counter += 1

        # Force-kill the threads to prevent zombies
        for thread in (trader_thread, gui_thread, exchange_thread):
            if thread.is_alive():
                thread._tstate_lock.release()
                thread._stop()

        print('\nThanks for using LiquiTrader!\n')
        sys.exit(0)

    # ----
    # Main thread loop
    while True:
        try:
            time.sleep(.1)

        except KeyboardInterrupt:
            shutdown()


if __name__ == '__main__':
    main(ipython=True)
