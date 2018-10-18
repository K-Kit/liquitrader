

def eight_decimal_format(value):
    return "{0:8f}".format(value)


def two_decimal_format(value):
    return "{0:2f}".format(value)

def time_format():
    pass

# use with functools  partial and pass quote price
def eight_decimal_with_usd(value, quote_price):
    return "{} (${})".format(eight_decimal_format(value), quote_price*value)

COLUMN_FORMATS = {'last_order_time': time_format,
                 'symbol': 'Symbol',
                 'avg_price': eight_decimal_format,
                 'close': eight_decimal_format,
                 'gain': two_decimal_format,
                 'quoteVolume': int,
                 'total_cost': eight_decimal_with_usd,
                 'current_value': eight_decimal_with_usd,
                 'dca_level': int,
                 'total': float,
                 'percentage': float
                  }
