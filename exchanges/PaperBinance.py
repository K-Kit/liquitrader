from exchanges.BinanceExchange import *
current_order_id = 0
def create_paper_order(symbol, order_type, side, amount, price, _quote_currency):
    """
            {
            'id':                '12345-67890:09876/54321', // string
            'datetime':          '2017-08-17 12:42:48.000', // ISO8601 datetime of 'timestamp' with milliseconds
            'timestamp':          1502962946216, // order placing/opening Unix timestamp in milliseconds
            'lastTradeTimestamp': 1502962956216, // Unix timestamp of the most recent trade on this order
            'status':     'open',         // 'open', 'closed', 'canceled'
            'symbol':     'ETH/BTC',      // symbol
            'type':       'limit',        // 'market', 'limit'
            'side':       'buy',          // 'buy', 'sell'
            'price':       0.06917684,    // float price in quote currency
            'amount':      1.5,           // ordered amount of base currency
            'filled':      1.1,           // filled amount of base currency
            'remaining':   0.4,           // remaining amount to fill
            'cost':        0.076094524,   // 'filled' * 'price' (filling price used where available)
            'trades':    [ ... ],         // a list of order trades/executions
            'fee': {                      // fee info, if available
                'currency': 'BTC',        // which currency the fee is (usually quote)
                'cost': 0.0009,           // the fee amount in that currency
                'rate': 0.002,            // the fee rate (if available)
            },
        'info': { ... },              // the original unparsed order structure as is
            :param symbol:
            :param order_type:
            :param side:
            :param amount:
            :param price:
            :return:
            """
    global current_order_id
    current_order_id += 1
    return {
        'id': current_order_id,
        'datetime': "",
        'timestamp': time.time() * 1000,
        'lastTradeTimestamp': time.time() * 1000,
        'status': "CLOSED",
        'symbol': symbol,
        'type': order_type,
        'side': side,
        'price': price,
        'amount': amount,
        'filled': amount,
        'remaining': 0,
        'cost': amount * price * 1.0005,
        'trades': [],
            'fee': {
            'currency': _quote_currency,
            'cost': amount*price*0.0005,
            'rate': 0.0005,
        }


    }

class PaperBinance(BinanceExchange):

    def __init__(self,
                 exchange_id: str,
                 quote_currency: str,
                 starting_balance: float,
                 access_keys: typing.Dict[typing.Union[str, str], typing.Union[str, str]],
                 candle_timeframes: typing.List[str]):

        super().__init__(exchange_id, quote_currency, access_keys, candle_timeframes)
        self.order_id = 0
        self.balance = starting_balance
        self.errors = []

    def update_balances(self):
        pass

    def place_order(self, symbol, order_type, side, amount, price):
        # self.pairs
        # self._quote_currency (for papertrading)
        # self.balance

        bought_price = self.pairs[symbol]['avg_price'] if side.lower() == 'sell' else None
        print(symbol, amount, self.pairs[symbol]['total'])

        order = create_paper_order(symbol, order_type, side, amount, price, self._quote_currency)
        print(order)

        if bought_price is not None:
            order['bought_price'] = bought_price

        if 'total' not in self.pairs[symbol]:
            self.pairs[symbol]['total'] = 0
        filled = order['filled']

        # fee will only be currency
        if self.pairs[symbol]['base'] == order['fee']['currency']:
            filled -= order['fee']['cost']

        # increment or decriment 'total' (quantity owned)
        self.pairs[symbol]['total'] += filled if side == 'buy' else - filled

        # increment or decriment total cost
        self.pairs[symbol]['total_cost'] += order['cost'] if side == 'buy' else - order['cost']

        # recalculate average price from total cost and amount
        try:
            self.pairs[symbol]['avg_price'] = self.pairs[symbol]['total_cost'] / self.pairs[symbol]['total']
        except ZeroDivisionError:
            self.pairs[symbol]['avg_price'] = None

        # update quote balance
        self.balance -= order['cost'] if side == 'buy' else - order['cost']

        # update last order time
        self.pairs[symbol]['last_order_time'] = int(time.time())
        # temp - will manually calc avg instead of calling update
        # self.update_balances()

        return order

if __name__ == '__main__':
    from dev_keys_binance import keys

    ex = PaperBinance('binance', 'USDT', 10,  {'public': keys.public, 'secret': keys.secret}, ['5m'])
    ex.initialize()

    # print(create_paper_order("ADA/ETH", 'limit', 'buy', 100, 1, 'ETH'))
    #
    # print(create_paper_order("ADA/ETH", 'limit', 'buy', 100, 1, 'ETH'))
    print(ex.place_order("ADA/USDT", 'limit', 'buy', 100, 1))
    print(ex.place_order("ADA/USDT", 'limit', 'buy', 100, 2))
    print(ex.place_order("ADA/USDT", 'limit', 'sell', 100, 1))