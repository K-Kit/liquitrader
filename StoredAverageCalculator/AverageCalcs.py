# this code isn't ready for use just started

# How much did we pay?
# How much is it worth (how much we paid * how many we have)
# When was the last average calculated (orderID), how much did we have a this point
# Users should be able to set current bought price which will be 'pinned' to the current trade ID and amount
# future averages will need to be calculated from the previous amount/price
#
# potential tests:
# make mock trade list for multiple buys
# class StoredAverageCalculator:
#
#     def __init__(self):
#         self.stored_averages = {}

# to get last trade id from an order
# order['trades'][-1]['info']['tradeId']

def get_last_buy_id(trades):
    for trade in reversed(trades):
        if trade['side'] == 'buy':
            return int(trade['id'])
    return None

def calc_average(trades, total_cost, total_amount, end_amount, last_buy_id=None):
    for trade in reversed(trades):
        cost = trade['cost'] if trade['side'] == 'buy' else -trade['cost']
        amount = trade['amount'] if trade['side'] == 'buy' else -trade['amount']
        # store last buy ID for calc from last ID to handle manual set bought price
        if trade['side'] == 'buy':
            if last_buy_id is None or int(trade['id']) > last_buy_id:
                last_buy_id = int(trade['id'])

        total_cost += cost
        total_amount += amount
        if total_amount <= end_amount * 1.02 and total_amount >= end_amount * 0.98:
            avg_price = total_cost / total_amount
            return {'total_cost': total_cost, 'amount': end_amount, 'avg_price': avg_price, 'last_id': last_buy_id}


    return None

def calc_average_price_from_hist(trades, amount_owned):
    # sum cost of trades + amount until within 2% of amount owned, this is to handle dust values
    # cost / amount = averages
    total_cost = 0
    total_amount = 0
    if amount_owned == 0: return None
    return calc_average(trades, total_cost, total_amount, amount_owned)


def calculate_from_previous_average(trades, starting_cost, starting_amount, last_buy_id, amount_owned):
    """
    In order to maintain the same average price after a partial sell order:
    update cost for current amount
    :param trades:
    :param starting_cost:
    :param starting_amount:
    :param amount_owned:
    :param last_buy_id:
    :return:
    """
    if get_last_buy_id(trades) == last_buy_id:
        avg_price = starting_cost / starting_amount
        total_cost = avg_price * amount_owned if amount_owned != starting_amount else starting_cost
        return {'total_cost': total_cost, 'amount': amount_owned, 'avg_price': avg_price, 'last_id': last_buy_id}

    else:
        total_cost = starting_cost
        total_amount = starting_amount
        new_trades = list(filter(lambda trade: int(trade['id']) > last_buy_id, trades))

        return calc_average(new_trades,starting_cost,starting_amount,amount_owned,last_buy_id)


def calculate_from_existing(trades, amount, previous_average_data):
    # just an easier way of calling calculate_from_previous_average
    return calculate_from_previous_average(trades, previous_average_data['total_cost'], previous_average_data['amount'], previous_average_data['last_id'], amount)

if __name__ == '__main__':
    import json
    storjtradepath = 'testdata/storjtrades-0.0011254.json'
    with open(storjtradepath, 'r') as f:
        trades = json.load(f)

    import pprint
    # pprint.pprint(trades[-1])

    t = calc_average_price_from_hist(trades,536)
    print(t)

# for tests we need list of dicts with: cost, side (buy/sell), amount, id