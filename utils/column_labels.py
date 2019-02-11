DEFAULT_COLUMNS = ['last_order_time', 'symbol', 'avg_price', 'close', 'gain', 'quoteVolume', 'total_cost',
                   'current_value', 'dca_level', 'total', 'percentage']

FRIENDLY_HOLDING_COLUMNS = ['Last Purchase Time', 'Symbol', 'Price', 'Bought Price', '% Change', 'Volume',
                            'Bought Value', 'Current Value', 'DCA Level', 'Amount', '24h Change']

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
