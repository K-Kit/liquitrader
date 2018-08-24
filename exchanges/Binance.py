from BaseExchange import *



class BinanceExchange(BaseExchange):

    def __init__(self, exchange_id, access_keys):
        super().__init__(exchange_id=exchange_id, access_keys=access_keys)

    def init_client_connection(self):
        super().init_client_connection()
        # =========================================
        # set default options for binance
        self.client.options['newOrderRespType'] = 'FULL'
        self.client.options['defaultTimeInForce'] = 'IOC'
        self.client.options['parseOrderToPrecision'] = True
        self.client.options['recvWindow'] = 10000


class keys:
    public_exchange_key = 'HPTpbOKj0konuPW72JozWGFDJbo0nK2rymbyObeX1vDSDSMZZd6vVosrA9dPFa1L'
    private_exchange_key = '4AuwPy6mVarrUqqECbyZSU9GrfOrInt6MIHdqvxHZWMaCXEjbSGGjBEuKmpCwPtb'


if __name__ == '__main__':
    ex = BinanceExchange('binance', {'public': keys.public_exchange_key, 'secret': keys.private_exchange_key})
    ex.init_client_connection()

    ex.pairs = ex.get_pairs('ETH')
    print(ex.pairs)
    from timeit import default_timer as timer

    start = timer()
    # ...

    asyncio.get_event_loop().run_until_complete(ex.load_all_candle_histories())
    end = timer()
    print(end - start)
    # asyncio.get_event_loop().run_until_complete(ex.ticker_upkeep(list(ex.pairs.keys())))
    #
    # asyncio.get_event_loop().run_until_complete(ex.candle_upkeep(list(ex.pairs.keys())))