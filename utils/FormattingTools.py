from functools import partial

def eight_decimal_format(value):
    return "{0:.8f}".format(value)


def two_decimal_format(value):
    return "{0:.2f}".format(value)

def time_format(val):
    return val

# use with functools  partial and pass quote price
def decimal_with_usd(value, quote_price=0, dec=8):
    return "{} (${})".format(eight_decimal_format(value), round(quote_price*value, 2))

COLUMN_FORMATS = {'last_order_time': str,
                 'symbol': None,
                 'avg_price': eight_decimal_format,
                 'close': eight_decimal_format,
                 'gain': partial(round, ndigits=2),
                 'quoteVolume': int,
                 'total_cost': decimal_with_usd,
                 'current_value': decimal_with_usd,
                 'dca_level': None,
                 'total': partial(round, ndigits=2),
                 'percentage': two_decimal_format
                  }


def prettify_dataframe(df, quote_price=200):
    usdformat = partial(decimal_with_usd, quote_price=quote_price)
    for column_name, format_func in COLUMN_FORMATS.items():
        if format_func is not None:
           df[column_name] = list(map(format_func, df[column_name])) if str(format_func) != str(decimal_with_usd) else \
                list(map(usdformat, df[column_name]))
    return df


# dfx = prettify_dataframe(bp.pairs_to_df())