import traceback
import datetime

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
    :param callback: function, params symbol, data
    :param interval: applies to  OHLCV socket to set candle interval
    :return:
    """

    @exchange.on('err')
    def websocket_error(err, conxid):  # pylint: disable=W0612
        error_stack = traceback.extract_stack()
        # TODO: log and handle errors https://github.com/firepol/ccxt-websockets-db-updater/issues/4
        print(f'{exchange.id}, {datetime.datetime.now()}, {error_stack}')

    @exchange.on(event)
    def websocket_ob(symbol, data):
        if interval:
            callback(symbol, data, interval)
        else:
            callback(symbol, data)

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

