# Fix from https://github.com/lfern/ccxt/blob/feature/websockets-multiple/examples/py/websocket-recover-connection.py

import asyncio
import sys
import traceback

import ccxt.async_support as ccxt  # noqa: E402


loop = asyncio.get_event_loop()
notRecoverableError = False
nextRecoverableErrorTimeout = None


async def doUnsubscribe(exchange,eventSymbols):  # noqa: E302
    try:
        await exchange.websocket_unsubscribe_all(eventSymbols)

    except (Exception, asyncio.TimeoutError) as ex:
        acceptable_errors = [
            'WebSocket opening handshake timeout (peer did not finish the opening handshake in time'
        ]

        if any(err in str(ex) for err in acceptable_errors):
            pass
        else:
            raise ex


async def doSubscribe(exchange, eventSymbols):  # noqa: E302
    global nextRecoverableErrorTimeout
    if notRecoverableError:
        return

    try:
        await exchange.websocket_subscribe_all(eventSymbols)

    except (Exception, asyncio.TimeoutError) as ex:
        acceptable_errors = [
            '(peer did not finish the opening handshake in time)',
            '(peer dropped the TCP connection without previous WebSocket closing handshake)'
        ]

        if any(err in str(ex) for err in acceptable_errors):
            pass
        else:
            raise ex

    except TimeoutError:
        pass


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

    @exchange.on('err')
    async def websocket_error(err, conxid=None):  # pylint: disable=W0612
        global notRecoverableError
        global loop
        global nextRecoverableErrorTimeout

        print(type(err).__name__ + ":" + str(err))
        traceback.print_tb(err.__traceback__)
        sys.stdout.flush()

        if conxid is not None:
            exchange.websocketClose(conxid)

        if isinstance(err, ccxt.NetworkError):
            await asyncio.sleep(5)
            try:
                if notRecoverableError:
                    return
                await doSubscribe(exchange, eventSymbols)

            except Exception as ex:
                print(f'Network error: {ex}')
                sys.stdout.flush()

        else:
            notRecoverableError = True
            if nextRecoverableErrorTimeout is not None:
                nextRecoverableErrorTimeout.cancel()
            await doUnsubscribe(exchange,eventSymbols)

            loop.stop()

    @exchange.on(event)
    def websocket_ob(symbol, data):
        if interval:
            callback(symbol, data, interval)
        else:
            callback(symbol, data)

    await exchange.loadMarkets()

    await doSubscribe(exchange, eventSymbols)

