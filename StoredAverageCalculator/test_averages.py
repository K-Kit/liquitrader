import pytest
import sys
sys.path.append('.')

sys.path.append('..')
from AverageCalcs import *

def test_one_trade_avg():
    trades = []
    buy = {"cost": 1, "amount": 5, "side": 'buy', 'id': '1'}
    trades.append(buy)
    average_data = calc_average_price_from_hist(trades,5)
    assert average_data['total_cost'] == 1
    assert average_data['amount'] == 5
    assert average_data['avg_price'] == 0.2
    assert average_data['last_id'] == 1


def test_two_trade_avg():
    trades = []
    buy = {"cost": 1, "amount": 5, "side": 'buy', 'id': '1'}
    trades.append(buy)
    average_data = calc_average_price_from_hist(trades, 5)
    dca_buy = {"cost": 3, "amount": 5, "side": 'buy', 'id': '2'}
    trades.append(dca_buy)
    new_avg_data = calculate_from_previous_average(trades, average_data['total_cost'], average_data['amount'], average_data['last_id'], 10)
    print(new_avg_data)
    assert new_avg_data['total_cost'] == 4
    assert new_avg_data['amount'] == 10
    assert new_avg_data['avg_price'] == 0.4
    assert new_avg_data['last_id'] == 2

def test_partial_sell():
    trades = []
    buy = {"cost": 1, "amount": 5, "side": 'buy', 'id': '1'}
    trades.append(buy)

    dca_buy = {"cost": 3, "amount": 5, "side": 'buy', 'id': '2'}
    trades.append(dca_buy)

    average_data = calc_average_price_from_hist(trades, 10)
    assert average_data['total_cost'] == 4
    assert average_data['amount'] == 10
    assert average_data['avg_price'] == 0.4
    assert average_data['last_id'] == 2

    part_sell = {"cost": 1, "amount": 1, "side": 'sell', 'id': '3'}
    trades.append(part_sell)
    # total cost = 1 + 3 - 1
    # amount = 5 + 5 - 1
    # last_id should be the last buy id, which is 2, even though the highest trade id is 3
    amount = 9
    new_avg_data = calculate_from_previous_average(trades, average_data['total_cost'], average_data['amount'], average_data['last_id'], 9)
    print(new_avg_data)
    # assert new_avg_data['total_cost'] == 4
    # assert new_avg_data['amount'] == 10
    # assert new_avg_data['avg_price'] == 0.4
    # assert new_avg_data['last_id'] == 2


if __name__ == '__main__':
    test_partial_sell()
    pytest.main()