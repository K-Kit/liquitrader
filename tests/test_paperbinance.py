from exchanges.PaperBinance import PaperBinance
from dev_keys_binance import keys

import pytest
import sys
sys.path.append('..')


def get_paper_instance(pairs=None, candles=None):
    if pairs is None:
        pairs = {
            'ADA/ETH': {"symbol": "ADA/ETH", "base": "ADA"}
        }

    if candles is None:
        candles = {}

        for pair in pairs:
            # assign default values for pairs
            candles[pair] = {}
            pairs[pair]['total'] = 0
            pairs[pair]['total_cost'] = 0
            pairs[pair]['avg_price'] = None
            pairs[pair]['dca_level'] = 0
            pairs[pair]['last_order_time'] = 0
            pairs[pair]['trades'] = []
            pairs[pair]['last_id'] = 0
            pairs[pair]['last_depth_check'] = 0

    instance = PaperBinance('binance',
                            'ETH',
                            10,
                            {'public': keys.public, 'secret': keys.secret},
                            ['5m'])

    instance.pairs = pairs
    instance.candles = candles

    return instance

# ----
def test_buy_order():
    instance = get_paper_instance()

    instance.place_order(amount=1, order_type='limit', price=2, side='buy', symbol='ADA/ETH')
    assert instance.pairs['ADA/ETH']['total'] == 1
    assert instance.pairs['ADA/ETH']['avg_price'] == 2 * 1.0005


def test_sell_order():
    instance = get_paper_instance()

    instance.place_order(amount=1, order_type='limit', price=2, side='buy', symbol='ADA/ETH')
    instance.place_order(amount=1, order_type='limit', price=2, side='sell', symbol='ADA/ETH')
    assert instance.pairs['ADA/ETH']['total'] == 0
    assert instance.pairs['ADA/ETH']['avg_price'] is None

def test_dca_buys():
    instance = get_paper_instance()

    instance.place_order(amount=1, order_type='limit', price=2, side='buy', symbol='ADA/ETH')
    assert instance.pairs['ADA/ETH']['total'] == 1
    assert instance.pairs['ADA/ETH']['avg_price'] == 2 * 1.0005

    instance.place_order(amount=1, order_type='limit', price=1, side='buy', symbol='ADA/ETH')
    assert instance.pairs['ADA/ETH']['total'] == 2
    assert instance.pairs['ADA/ETH']['avg_price'] == 1.5 * 1.0005
    assert instance.pairs['ADA/ETH']['total_cost'] == 3 * 1.0005

    instance.place_order(amount=2, order_type='limit', price=1, side='buy', symbol='ADA/ETH')
    assert instance.pairs['ADA/ETH']['total'] == 4
    assert instance.pairs['ADA/ETH']['avg_price'] == 1.25 * 1.0005
    assert instance.pairs['ADA/ETH']['total_cost'] == 5 * 1.0005

# ========
if __name__ == '__main__':
    pytest.main([__file__])
