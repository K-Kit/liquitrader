import pandas as pd

def get_percent_change(current:float, bought:float):
    if bought is None or bought == 0: return 0
    return (current-bought)/bought*100

def get_current_value(price:float, amount:float):
    return price*amount

# returns false the trade would not exceed min buy balance (buy on false)
def exceeds_min_balance(balance, min_buy_balance, price, amount):
    return balance - (price*amount) < min_buy_balance

#check min balance, max pairs, quote change, market change, trading enabled, blacklist, whitelist, 24h change

def below_max_pairs(current_pairs, max_pairs):
    return current_pairs < max_pairs or max_pairs == 0

def below_max_change(change, max_change):
    return change < max_change or max_change == 0

def above_min_change(change, min_change):
    return change > min_change or min_change == 0

def is_blacklisted(pair, blacklist):
    return pair in blacklist

def is_whitelisted(pair, whitelist):
    return pair in whitelist or 'ALL' in whitelist or 'all' in whitelist


def get_average_market_change(pairs):
    try:
        return pd.DataFrame.from_dict(pairs, orient='index').percentage.mean()
    except Exception as ex:
        print(ex)
        return 0


def in_max_spread(close, fill_price, max_spread):
    if max_spread == 0: max_spread = 1
    return abs((close - fill_price) / fill_price) <= max_spread


def in_range(change, min, max):
    above_min = above_min_change(change, min)
    below_max = below_max_change(change, max)
    if min == 0:
        return below_max
    elif max == 0:
        return above_min
    elif min == 0 and max == 0:
        return True
    else:
        return below_max and above_min

def get_current_pending_value(pairs, balance):
    return pd.DataFrame.from_dict(pairs, orient='index').total_cost.sum() + balance


if __name__ == '__main__':
    # false
    print(below_max_pairs(10,10))
    # true
    print(below_max_pairs(9,10))
    # false
    print(below_max_pairs(11,10))
    # true
    print(below_max_pairs(11,0))