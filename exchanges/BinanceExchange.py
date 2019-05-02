
import json
import time
import traceback

from exchanges.GenericExchange import *

import asyncio

from utils.CandleTools import candles_to_df, candle_tic_to_df
# import SocketManager
from SocketManager import subscribe_ws


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
    def handle_candle_socket(self, symbol, candle_data, candle_period):
        # update candlestick data for appropriate candle_period
        candle = candle_tic_to_df(candle_data)
        if symbol in self.pairs:
            try:
                self.candles[symbol][candle_period].loc[candle.index[0]] = candle.iloc[0]

            except Exception as ex:
                print("binance.handle_candle_socket", ex, symbol,candle_data)
                self.reload_single_candle_history(symbol)

    # ----
    def handle_ticker_socket(self, symbol, data):
        # renamed what used to be pair.price to pair['close'] to follow CCXT conventions

        if symbol in self.pairs:
            data['close'] = float(data['info']['c'])
            self.pairs[symbol].update(data)

        elif 'USDT' in symbol:
            self.quote_change = float(data['percentage'])
            self.quote_price = float(data['close'])

    # ----
    def handle_depth_socket(self, symbol, data):

        if symbol in self.pairs:
            pair = self.pairs[symbol]
            pair['last_depth_socket_tick'] = time.time()
            pair['asks'] = data['asks']
            pair['bids'] = data['bids']

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
        # if pair['last_depth_check'] < pair['last_depth_socket_tick']:
        #     pair['last_depth_check'] = time.time()
        return pair['asks'] if side.upper() == 'BUY' else pair['bids']

        # elif time.time() - pair['last_depth_check'] > 0.5:
        #     depth = self._client.fetch_order_book(symbol)
        #     pair['last_depth_check'] = time.time()
        #     return depth['asks'] if side.upper() == 'BUY' else depth['bids']

        # else:
        #     return None




    # ----
    async def initialize(self):
        # this may want to be split up
        self._init_client_connection()
        self._client.load_markets()

        await super().initialize()

        time.sleep(1)
        # self.start_sockets()

        self.update_balances()

    # ----
    def start(self):
        """
        Main loop for controlling class
        Checks to see if sockets are dead and restarts them as necessary
        Makes calls to upkeep methods
        """
        if not self._loop:
            self._loop = asyncio.get_event_loop()
        self._loop.create_task(self._quote_change_upkeep())
        self._loop.create_task(self._balances_upkeep())
        self._loop.create_task(self._socket_upkeep())
        pairs_list = list(self.pairs.keys())
        self._loop.create_task(subscribe_ws('ob', self._client_async, pairs_list, callback=self.handle_depth_socket))
        self._loop.create_task(
            subscribe_ws('ticker', self._client_async, pairs_list, callback=self.handle_ticker_socket))
        for interval in self._candle_timeframes:
            self._loop.create_task(subscribe_ws('ohlcv', self._client_async, pairs_list, interval=interval,
                                          callback=self.handle_candle_socket))
        self._loop.run_forever()

    # ----
    def stop(self):
        from twisted.internet import reactor

        # Kill Binance library's Twisted server
        reactor.callFromThread(lambda: reactor.stop())

        for p in reactor.getDelayedCalls():
            if p.active():
                p.cancel()

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
        raise('kyles dumbass broke this with websocket changes, will fix eventually')
        # print('detected closed sockets, re-opening connection')
        # self.socket_manager.close()
        # self.init_socket_manager(self._access_keys['public'], self._access_keys['secret'])
        # self.last_candle_update_time = time.time()+10
        # self.last_depth_update_time = time.time()+10
        # self.last_ticker_update_time = time.time()+10
        # self.start_sockets()

    # ----
    def check_sockets(self):

        raise('kyles dumbass broke this with websocket changes, will fix eventually')
        # now = time.time()
        #
        # def not_stale(now, last_check):
        #     if last_check is None:
        #         return True
        #     return now-last_check < 15
        #
        # deltas = [
        #     not_stale(now, self.last_candle_update_time),
        #     not_stale(now, self.last_depth_update_time),
        #     not_stale(now, self.last_ticker_update_time)
        # ]
        # if not all(deltas):
        #     self.restart_sockets()



# ----
# if __name__ == '__main__':
#     from dev_keys_binance import keys
#     ex = BinanceExchange('binance', 'ETH', 5, {'public': keys.public, 'secret': keys.secret}, ['5m'])
#     asyncio.get_event_loop().run_until_complete(ex.initialize())
#     ex.update_balances()
#     # ex.start()
#     client = ex._client
