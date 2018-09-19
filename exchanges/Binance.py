import asyncio
import json
import time

from exchanges.GenericExchange import *
from binance.client import Client
from binance.websockets import BinanceSocketManager

from utils.CandleTools import candles_to_df, candle_tic_to_df

def gen_socket_list(pairs: dict, timeframes: list):
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
                 access_keys: typing.Dict[typing.Union[str, str], typing.Union[str, str]],
                 candle_timeframes: typing.List[str]):

        super().__init__(exchange_id, quote_currency, access_keys, candle_timeframes)

        self.socket_manager = None

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
        self._client.options['recvWindow'] = 10000

    # ----
    def init_socket_manager(self, public, secret):
        self.socket_manager = BinanceSocketManager(Client(public, secret))
        self.socket_manager.start()

    # ----
    def process_multiplex_socket(self, msg):
        # this callback recieves all socket messages and dispatches to the appropriate handler function
        # todo add error handling, restart, check for last_update time lag on each socket
        if 'e' in msg and msg['e'] == 'error':
            print('implement socket error handleing', msg)
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
            self.pairs[symbol]['candlesticks'][candle_period].loc[candle.index[0]] = candle.iloc[0]

    # ----
    def handle_ticker_socket(self, msg, symbol):
        # renamed what used to be pair.price to pair['close'] to follow CCXT conventions
        if 'e' in msg and msg['e'] == 'error':
            print('implement socket error handling', msg)
            return

        elif symbol in self.pairs:
            self.pairs[symbol]['close'] = msg['c']
            self.pairs[symbol]['quoteVolume'] = msg['q']
            self.pairs[symbol]['percentage'] = msg['P']

    # ----
    def handle_depth_socket(self, msg, symbol):
        # update bids/asks: parse bids/asks to float
        if 'e' in msg and msg['e'] == 'error':
            print('implement socket error handling', msg)
            return

        if symbol in self.pairs:
            pair = self.pairs[symbol]
            pair['asks'] = [[float(ask[0]), float(ask[1])] for ask in msg['asks']]
            pair['bids'] = [[float(bid[0]), float(bid[1])] for bid in msg['bids']]

    # ----
    def initialize(self):
        # this may want to be split up
        self._init_client_connection()
        self._client.load_markets()
        self.init_socket_manager(self._access_keys['public'],self._access_keys['secret'])

        super().initialize()

        asyncio.get_event_loop().run_until_complete(
            self.load_all_candle_histories(num_candles=500))

        time.sleep(1)

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

        self._balances = self.update_balances()

    # ----
    def start(self):
        """
        Main loop for controlling class
        Checks to see if sockets are dead and restarts them as necessary
        Makes calls to upkeep methods
        """

        pass

    # ----
    def stop(self):
        self.socket_manager.close()

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


# ----
if __name__ == '__main__':
    from dev_keys_binance import keys
    ex = BinanceExchange('binance', 'ETH', {'public': keys.public, 'secret': keys.secret}, ['5m'])
    ex.initialize()
    ex.update_balances()
