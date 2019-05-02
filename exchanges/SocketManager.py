import traceback
import datetime
import sys
import asyncio

async def subscribe_ws(event, exchange, symbols, limit=20, debug=False, verbose=False, order_books=None, callback=None, interval=None):
    """
    Subscribe websockets channels of many symbols in the same exchange
    :param event: 'ob' for orderbook updates, 'ticker' for ticker, 'trade' for trades, refer to CCXT WS documentation
    :param exchange: CCXT exchange instance
    :param symbols: list of symbols e.g. ['btc/usd', 'trx/btc']
    :param limit: order books limit, e.g. 1 for just the best price, 5 for the 5 best prices etc.
    :param debug: if "True", prints 1 ask and 1 bid
    :param verbose: if "True", prints the order books using pretty print
    :param order_books: "buffer" dictionary containing the order books (it is used to update the DB)
    :return:
    """



    @exchange.on('err')
    async def websocket_error(err, conxid):  # pylint: disable=W0612
        error_stack = traceback.extract_stack()
        # TODO: log and handle errors https://github.com/firepol/ccxt-websockets-db-updater/issues/4
        print(f'{exchange.id}, {datetime.datetime.now()}, {error_stack}')

    @exchange.on(event)
    def websocket_ob(symbol, data):
        if interval:
            callback(symbol, data, interval)
        else:
            callback(symbol, data)

        # TODO: check if there are exchanges ending with 2 & in that case don't truncate the last character
        exchange_name = exchange.id
        if exchange.id.endswith('2'):
            exchange_name = exchange.id[:-1]

        if order_books:
            order_books[exchange_name][symbol] = {'asks': asks, 'bids': bids, 'datetime': ob_datetime}

    sys.stdout.flush()

    eventSymbols = []
    for symbol in symbols:
        eventSymbols.append({
            "event": event,
            "symbol": symbol,
            "params": {
                'limit': limit,
                'interval': interval
            }
        })

    await exchange.websocket_subscribe_all(eventSymbols)


if __name__ == '__main__':
    from gui.gui_server import get_keys
    import BinanceExchange
    keys = get_keys()
    exchange = BinanceExchange.BinanceExchange('binance', 'ETH', 3, keys,['5m', '15m'])
    ccxt_ex = exchange._client_async
    # loop = exchange._loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(exchange.initialize())
    except:
        pass
    exchange._initialize_pairs()
    print('initialized')
    try:
        loop.create_task(subscribe_ws('ob', ccxt_ex, list(exchange.pairs.keys())))
        # loop.create_task(subscribe_ws('ticker', ccxt_ex, list(exchange.pairs.keys())))
        # loop.create_task(subscribe_ws('ohlcv', ccxt_ex, list(exchange.pairs.keys()), interval='5m'))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()
    # loop.stop()
    # loop.close()
    print("after complete")