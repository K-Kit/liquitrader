import asyncio
import json
import time
import traceback

from exchanges.GenericExchange import *

import binance
from binance import client, websockets

import twisted


Client = binance.client.Client
BinanceSocketManager = binance.websockets.BinanceSocketManager

#from binance.client import Client
#from binance.websockets import BinanceSocketManager

from utils.CandleTools import candles_to_df, candle_tic_to_df


def gen_socket_list(pairs: dict, timeframes: set):
    # creates list of socket streams to subscribe to
    candles = ['{}@kline_{}'.format(pair['id'].lower(), timeframe) for timeframe in timeframes for pair in pairs.values()]
    depth = ['{}@depth20'.format(pair['id'].lower()) for pair in pairs.values()]
    tickers = ['{}@ticker'.format(pair['id'].lower()) for pair in pairs.values()]
    return candles, depth, tickers


# TODO check last socket update time and restart if needed
class BinanceExchange(GenericExchange):

    def __init__(self,
                 exchange_id: str,
                 quote_currency: str,
                 starting_balance: float,
                 access_keys: typing.Dict[typing.Union[str, str], typing.Union[str, str]],
                 candle_timeframes: typing.List[str]):

        super().__init__(exchange_id, quote_currency, starting_balance, access_keys, candle_timeframes)
        self._socket_upkeep_schedule = 60

        self.socket_manager = None
        self.quote_currency = quote_currency.upper()
        self.candle_socket = None
        self.ticker_socket = None
        self.depth_socket = None

        self.last_candle_update_time = None
        self.last_depth_update_time = None
        self.last_ticker_update_time = None

    # ----
    def _init_client_connection(self):
        super()._init_client_connection()

        # =========================================
        # set default options for binance

        # FULL order response to include trade list
        self._client.options['newOrderRespType'] = 'FULL'

        # default order time IMMEDIATE OR CANCEL
        self._client.options['defaultTimeInForce'] = 'IOC'

        # so we dont have to mess with foat/str precision per pair
        self._client.options['parseOrderToPrecision'] = True
        self._client.options['recvWindow'] = 100000

    # ----
    def init_socket_manager(self, public, secret):
        self.socket_manager = BinanceSocketManager(Client(public, secret))
        self.socket_manager.setDaemon(True)

    # ----
    def process_multiplex_socket(self, msg):
        # this callback recieves all socket messages and dispatches to the appropriate handler function
        # todo add error handling, restart, check for last_update time lag on each socket
        if 'e' in msg and msg['e'] == 'error':
            return

        if 'kline' in msg['stream']:
            self.handle_candle_socket(msg['data']['k'], self.parse_stream_name(msg['stream']), self.parse_candle_period(msg['stream']))
            self.last_candle_update_time = time.time()

        elif 'depth' in msg['stream']:
            self.last_depth_update_time = time.time()
            self.handle_depth_socket(msg['data'], self.parse_stream_name(msg['stream']))

        elif 'ticker' in msg['stream']:
            self.last_ticker_update_time = time.time()
            self.handle_ticker_socket(msg['data'], self.parse_stream_name(msg['stream']))

        else:
            print('unknown socket res: {}'.format(msg))

    # ----
    def handle_candle_socket(self, msg, symbol, candle_period):
        # update candlestick data for appropriate candle_period
        if 'e' in msg and msg['e'] == 'error':
            print('implement socket error handling', msg)
            return

        candle = candle_tic_to_df([msg['t'], msg['o'], msg['h'], msg['l'], msg['c'], msg['v']])
        if symbol in self.pairs:
            try:
                self.candles[symbol][candle_period].loc[candle.index[0]] = candle.iloc[0]

            except Exception as ex:
                print("binance.handle_candle_socket", ex, msg)
                self.reload_single_candle_history(symbol)

    # ----
    def handle_ticker_socket(self, msg, symbol):
        # renamed what used to be pair.price to pair['close'] to follow CCXT conventions
        if 'e' in msg and msg['e'] == 'error':
            print('implement socket error handling', msg)
            return

        elif symbol in self.pairs:
            self.pairs[symbol]['close'] = float(msg['c'])
            self.pairs[symbol]['bid'] = float(msg['b'])
            self.pairs[symbol]['ask'] = float(msg['a'])
            self.pairs[symbol]['quoteVolume'] = float(msg['q'])
            self.pairs[symbol]['percentage'] = float(msg['P'])

        elif symbol == self.quote_currency + '/USDT':
            self.quote_change = float(msg['P'])
            self.quote_price = float(msg['c'])

    # ----
    def handle_depth_socket(self, msg, symbol):
        # update bids/asks: parse bids/asks to float
        if 'e' in msg and msg['e'] == 'error':
            print('implement socket error handling', msg)
            return

        if symbol in self.pairs:
            pair = self.pairs[symbol]
            pair['last_depth_socket_tick'] = time.time()
            pair['asks'] = [[float(ask[0]), float(ask[1])] for ask in msg['asks']]
            pair['bids'] = [[float(bid[0]), float(bid[1])] for bid in msg['bids']]

    # ----
    def get_depth(self, symbol, side):
        """
        get bids or asks for pair. if side == buy, return asks, else bids
        if socket has ticked since last depth check, return pair[bids/asks]
        else fetch fresh orderbook and return
        :param symbol:
        :param side:
        :return:
        """
        pair = self.pairs[symbol]
        if pair['last_depth_check'] < pair['last_depth_socket_tick']:
            pair['last_depth_check'] = time.time()
            return pair['asks'] if side.upper() == 'BUY' else pair['bids']

        elif time.time() - pair['last_depth_check'] > 0.5:
            depth = self._client.fetch_order_book(symbol)
            pair['last_depth_check'] = time.time()
            return depth['asks'] if side.upper() == 'BUY' else depth['bids']

        else:
            return None

    
    # ----
    def start_sockets(self):
        def gen_socket_list(pairs: dict, timeframes: set):
            # creates list of socket streams to subscribe to
            candles = ['{}@kline_{}'.format(pair['id'].lower(), timeframe) for timeframe in timeframes for pair in
                       pairs.values()]
            depth = ['{}@depth20'.format(pair['id'].lower()) for pair in pairs.values()]
            tickers = ['{}@ticker'.format(pair['id'].lower()) for pair in pairs.values()]
            return candles, depth, tickers

        # generate list of stream names to start in multiplex socket
        candle_sockets, depth_sockets, ticker_sockets = gen_socket_list(self.pairs, self._candle_timeframes)

        # store connection keys self.candle_sock
        # time.sleep due to issues opening all at same time

        # TODO: Look into doing this without sleeps
        self.candle_socket = self.socket_manager.start_multiplex_socket(candle_sockets, self.process_multiplex_socket)
        time.sleep(1)

        self.depth_socket = self.socket_manager.start_multiplex_socket(depth_sockets, self.process_multiplex_socket)

        time.sleep(1)
        self.ticker_socket = self.socket_manager.start_multiplex_socket(ticker_sockets, self.process_multiplex_socket)
        try:
            self.socket_manager.start()
        except Exception as ex:
            print(ex)

    # ----
    async def initialize(self):
        # this may want to be split up
        self._init_client_connection()
        self._client.load_markets()
        self.init_socket_manager(self._access_keys['public'], self._access_keys['secret'])

        await super().initialize()

        time.sleep(1)
        self.start_sockets()

        self.update_balances()

    # ----
    def start(self):
        """
        Main loop for controlling class
        Checks to see if sockets are dead and restarts them as necessary
        Makes calls to upkeep methods
        """
        self._loop.create_task(self._quote_change_upkeep())
        self._loop.create_task(self._balances_upkeep())
        self._loop.create_task(self._socket_upkeep())
        self._loop.run_forever()

    # ----
    def stop(self):
        from twisted.internet import reactor

        # Kill Binance library's Twisted server
        reactor.callFromThread(lambda: reactor.stop())

        for p in reactor.getDelayedCalls():
            if p.active():
                p.cancel()

        try:
            # Close websocket connections
            self.socket_manager.close()

        except Exception as _ex:
            print(str(_ex))

        new_loop = asyncio.new_event_loop()
        new_loop.run_until_complete(super().stop())

    # ----
    def parse_stream_name(self, stream_name):
        # split the stream name to get and format symbol for dict access
        # need to find better way to fix removed / changed names for main net swaps
        stream = stream_name.split('@')[0]
        return self._client.markets_by_id[stream.upper()]['symbol']

    # ----
    @staticmethod
    def parse_candle_period(stream_name):
        # get candle period from stream name to associate candle period
        return stream_name.split('_')[1]

    # --
    async def _socket_upkeep(self):
        """
        update candle history during runtime - see binance klines socket handler
        candle history will fetch most recent candle for all timeframes and assign to end of candles dataframe
        """

        while 1:
            self.check_sockets()
            await asyncio.sleep(self._socket_upkeep_schedule)

    def restart_sockets(self):
        print('detected closed sockets, re-opening connection')
        self.socket_manager.close()
        self.init_socket_manager(self._access_keys['public'], self._access_keys['secret'])
        self.last_candle_update_time = time.time()+10
        self.last_depth_update_time = time.time()+10
        self.last_ticker_update_time = time.time()+10
        self.start_sockets()

    # ----
    def check_sockets(self):
        now = time.time()

        def not_stale(now, last_check):
            if last_check is None:
                return True
            return now-last_check < 15

        deltas = [
            not_stale(now, self.last_candle_update_time),
            not_stale(now, self.last_depth_update_time),
            not_stale(now, self.last_ticker_update_time)
        ]
        if not all(deltas):
            self.restart_sockets()



# ----
# if __name__ == '__main__':
#     from dev_keys_binance import keys
#     ex = BinanceExchange('binance', 'ETH', 5, {'public': keys.public, 'secret': keys.secret}, ['5m'])
#     asyncio.get_event_loop().run_until_complete(ex.initialize())
#     ex.update_balances()
#     # ex.start()
#     client = ex._client
