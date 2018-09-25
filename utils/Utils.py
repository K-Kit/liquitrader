def get_percent_change(current:float, bought:float):
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


if __name__ == '__main__':
    print(exceeds_min_balance(1, 1, 1, 1))
    print(exceeds_min_balance(2.1, 1, 1, 1))

    print(exceeds_min_balance(2, 1, 1, 1))