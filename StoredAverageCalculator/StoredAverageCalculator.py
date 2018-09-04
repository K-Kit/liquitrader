# this code isn't ready for use just started

class StoredAverageCalculator:

    def __init__(self):
        self.stored_averages = {}

    def calc_average_price_from_hist(self, trades, amount_owned, last_buy_id=None):
        # sum cost of trades + amount until within 2% of amount owned, this is to handle dust values
        # cost / amount = averages
        total_cost = 0
        total_amount = 0

        for trade in reversed(trades):
            cost = trade['cost'] if trade['side'] == 'buy' else -trade['cost']
            amount = trade['amount'] if trade['side'] == 'buy' else -trade['amount']
            # store last buy ID for calc from last ID to handle manual set bought price
            if trade['side'] == 'buy' and last_buy_id == None:
                last_buy_id = int(trade['id'])

            total_cost += cost
            total_amount += amount
            if total_amount <= amount_owned * 1.02 and total_amount >= total_amount * 0.98:
                return total_cost / total_amount
        return None


if __name__ == '__main__':
    import json
    storjtradepath = 'testdata/storjtrades-0.0011254.json'
    with open(storjtradepath, 'r') as f:
        trades = json.load(f)