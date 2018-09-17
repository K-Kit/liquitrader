import pytest
import sys
sys.path.append('.')

sys.path.append('..')
from utils.AverageCalcs import *

# this can be moved to tests later, however the other tests make a
# ton of api calls, which i didnt want to deal with right now

buy = {"cost": 1, "amount": 5, "side": 'buy', 'id': '1'}
dca_buy = {"cost": 3, "amount": 5, "side": 'buy', 'id': '2'}
part_sell = {"cost": 1, "amount": 2, "side": 'sell', 'id': '3'}

one_trade = [buy]

dca_trades = [buy, dca_buy]

partial_sell_trades = [buy, dca_buy, part_sell]

def test_one_trade_avg():
    trades = []
    buy = {"cost": 1, "amount": 5, "side": 'buy', 'id': '1'}
    trades.append(buy)
    average_data = calc_average_price_from_hist(trades,5)
    assert average_data['total_cost'] == 1
    assert average_data['amount'] == 5
    assert average_data['avg_price'] == 0.2
    assert average_data['last_id'] == 1

def test_one_trade_invalid_amount():
    # correct amount: 5, calculating for 3 should return none
    average_data = calc_average_price_from_hist(one_trade, 3)
    assert average_data is None

def test_two_trade_avg():
    average_data = calc_average_price_from_hist(one_trade, 5)
    new_avg_data = calculate_from_previous_average(dca_trades, average_data['total_cost'], average_data['amount'], average_data['last_id'], 10)
    # cost = 1 + 3
    assert new_avg_data['total_cost'] == 4
    # amount = 5 + 5
    assert new_avg_data['amount'] == 10
    # 4 / 10
    assert new_avg_data['avg_price'] == 0.4
    assert new_avg_data['last_id'] == 2

def test_partial_sell():
    average_data = calc_average_price_from_hist(dca_trades, 10)
    # total cost = 1 + 3 - 1
    # amount = 5 + 5 - 1
    # last_id should be the last buy id, which is 2, even though the highest trade id is 3
    amount = average_data['amount'] - part_sell['amount']
    new_avg_data = calculate_from_previous_average(partial_sell_trades, average_data['total_cost'], average_data['amount'], average_data['last_id'], amount)
    assert new_avg_data['total_cost'] == 3.2
    assert new_avg_data['amount'] == amount
    assert new_avg_data['avg_price'] == 0.4
    assert new_avg_data['last_id'] == 2

def test_hist_average_alias():
    average_data = calc_average_price_from_hist(dca_trades, 10)
    # total cost = 1 + 3 - 1
    # amount = 5 + 5 - 1
    # last_id should be the last buy id, which is 2, even though the highest trade id is 3
    amount = average_data['amount'] - part_sell['amount']
    new_avg_data = calculate_from_existing(partial_sell_trades, amount, average_data)
    assert new_avg_data['total_cost'] == 3.2
    assert new_avg_data['amount'] == amount
    assert new_avg_data['avg_price'] == 0.4
    assert new_avg_data['last_id'] == 2

if __name__ == '__main__':
    test_partial_sell()
    pytest.main()

