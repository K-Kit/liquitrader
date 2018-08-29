import asyncio
import json
from BaseExchange import *
from binance.client import Client
from binance.websockets import BinanceSocketManager

from Utils.CandleTools import candles_to_df, candle_tic_to_df

def gen_socket_list(pairs, timeframes):
    # creates list of socket streams to subscribe to
    candles = ['{}@kline_{}'.format(pair['id'].lower(), timeframe) for timeframe in timeframes for pair in pairs.values()]
    depth = ['{}@depth20'.format(pair['id'].lower()) for pair in pairs.values()]
    tickers = ['{}@ticker'.format(pair['id'].lower()) for pair in pairs.values()]
    return candles, depth, tickers

class BinanceExchange(BaseExchange):

    def __init__(self, exchange_id, access_keys):
        super().__init__(exchange_id=exchange_id, access_keys=access_keys)
        self.res = []
        self.rest = []
        self.resc = []
        self.last_update_time = None

    def init_client_connection(self):
        super().init_client_connection()

        # =========================================
        # set default options for binance
        self.client.options['newOrderRespType'] = 'FULL'
        self.client.options['defaultTimeInForce'] = 'IOC'
        self.client.options['parseOrderToPrecision'] = True
        self.client.options['recvWindow'] = 10000

    def init_socket_manager(self, public, secret):
        self.socket_manager = BinanceSocketManager(Client(public, secret))
        # self.socket_manager.start()

    def process_multiplex_socket(self, msg):

        if 'e' in msg and msg['e'] == 'error':
            print('implement socket error handleing', msg)
            return

        if 'kline' in msg['stream']:
            self.handle_candle_socket(msg['data'], self.parse_stream_name(msg['stream']), self.parse_candle_period(msg['stream']))
            self.last_candle_update_time = time.time()
            self.resc.append(msg['data'])

        elif 'depth' in msg['stream']:
            self.res.append(msg['data'])
            self.last_depth_update_time = time.time()
            self.handle_depth_socket(msg['data'], self.parse_stream_name(msg['stream']))

        elif 'ticker' in msg['stream']:
            self.rest.append(msg['data'])
            self.last_ticker_update_time = time.time()
            self.handle_ticker_socket(msg['data'], self.parse_stream_name(msg['stream']))

        else:
            print('unknown socket res: {}'.format(msg))




    def handle_candle_socket(self, msg, symbol, candle_period):
        if 'e' in msg and msg['e'] == 'error':
            print('implement socket error handleing', msg)
            return
        candle = candle_tic_to_df(msg)
        if symbol in self.pairs: self.pairs[symbol]['candlesticks'][candle_period].loc[candle.index[0]] = candle.iloc[0]


    def handle_ticker_socket(self, msg, symbol):
        if 'e' in msg and msg['e'] == 'error':
            print('implement socket error handleing', msg)
            return
        elif symbol in self.pairs:
            self.pairs[symbol]['close'] = msg['c']
            self.pairs[symbol]['quoteVolume'] = msg['q']
            self.pairs[symbol]['percentage'] = msg['P']

    def handle_depth_socket(self, msg, symbol):
        if 'e' in msg and msg['e'] == 'error':
            print('implement socket error handleing', msg)
            return
        if symbol in self.pairs: self.pairs[symbol]['orderbook'] = msg


    def save(self):
        with open('../pairs_data.json', 'w') as f:
            json.dump(self.pairs, f)

    @staticmethod
    def parse_stream_name(stream_name):
        stream = stream_name.split('@')[0]
        market = stream[-3:] if stream[-1] != 't' else stream[-4:]
        symbol = stream[:-len(market)]
        if symbol == 'bcc':
            symbol = 'BCH'
        elif symbol == 'yoyo':
            symbol = 'YOYOW'
        return '{}/{}'.format(symbol.upper(), market.upper())

    @staticmethod
    def parse_candle_period(stream_name):
        return stream_name.split('_')[1]



class keys:
    public = 'HPTpbOKj0konuPW72JozWGFDJbo0nK2rymbyObeX1vDSDSMZZd6vVosrA9dPFa1L'
    secret = '4AuwPy6mVarrUqqECbyZSU9GrfOrInt6MIHdqvxHZWMaCXEjbSGGjBEuKmpCwPtb'


if __name__ == '__main__':
    ex = BinanceExchange('binance', {'public': keys.public, 'secret': keys.secret})
    ex.init_client_connection()
    ex.init_socket_manager(keys.public, keys.secret)
    ex.pairs = ex.get_pairs('USDT')
    print(ex.pairs.keys())
    print(len(ex.pairs))
    timeframes = ['5m', '15m']
    asyncio.get_event_loop().run_until_complete(ex.load_all_candle_histories(timeframes=timeframes, num_candles=200))
    time.sleep(1)
    candle_sockets, depth_sockets, ticker_sockets = gen_socket_list(ex.pairs, timeframes)

    ex.socket_manager.start()

    ex.socket_manager.start_multiplex_socket(candle_sockets, ex.process_multiplex_socket)
    time.sleep(1)

    ex.socket_manager.start_multiplex_socket(depth_sockets, ex.process_multiplex_socket)

    time.sleep(1)
    ex.socket_manager.start_multiplex_socket(ticker_sockets, ex.process_multiplex_socket)
    # from timeit import default_timer as timer
    #
    # start = timer()
    # # ...
    #
    # asyncio.get_event_loop().run_until_complete(ex.load_all_candle_histories(timeframes= ['5m', '15m'], num_candles=100))
    # end = timer()
    #
    # print(len(ex.pairs))
    # print(end - start)
