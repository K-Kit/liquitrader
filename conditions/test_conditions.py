import sys
sys.path.append('..')
from BuyCondition import *
from DCABuyCondition import *
from SellCondition import *
import pytest
# todo comment and come up with better more robust tests
mfi_30_change_3_5m = {'value': 'MFI', 'change_over': 3, 'candle_count': 30, 'candle_period': '5m'}
mfi_30_15m = {'value': 'MFI', 'candle_count': "30", 'candle_period': '15m'}
mfi_30m = {'value': 'MFI', 'candle_period': '30m'}
lowerband_5m = {'value': 'lowerband', 'candle_period': '5m'}
staticval = {'value': 4}
percentval = {'value': '5%'}
price = {'value': 'price'}
cdlharami = {'value': 'CDLHARAMI'}

# test conditions
condition_1 = {'left': mfi_30m, 'op': '>', 'right': staticval}
condition_2 = {'left': mfi_30m, 'op': '<', 'right': staticval}
condition_3 = {'left': mfi_30m, 'op': 'cross_up', 'right': staticval, 'cross_candles': 3}
condition_4 = {'left': mfi_30m, 'op': 'cross_down', 'right': staticval, 'cross_candles': 3}
condition_5 = {'op': 'min_volume', 'right': 4}
condition_6 = {'op': 'min_profit', 'right': 1}

# pair, indicators
indicators1 = {'MFI_30_15m': [1,2,3,4,5], 'MFI_30_5m': [1,2,3,4,5], 'MFI_30m': [1,2,3,4,5]}
pair1 = {'symbol': 'ADA/ETH', 'close': 1, 'quoteVolume': 1000, 'bought_value': 1, 'current_value': 1.0, 'total_cost': 1, 'total': 1}

strategy = {}
# 1 and 3 are true with the test data
strategy['conditions'] = [condition_1]
strategy['trailing %'] = 0.1
strategy['sell_value'] = 1
strategy['trailing %'] = 0.1
strategy['buy_value'] = 0.02
strategy['max_dca_level'] = 5
strategy['dca_strategy'] = {"default": {"trigger": -3, "percentage": 100},
                            "0": {"trigger": -5, "percentage": 50},
                            "3":{"trigger": -2, "percentage": 25}}

cond = SellCondition(strategy)

def test_buy_strategy():
    pair = pair1.copy()
    indicators = indicators1.copy()
    buystrat = BuyCondition(strategy)
    eval = buystrat.evaluate(pair, indicators)
    assert 'ADA/ETH' in buystrat.pairs_trailing
    assert eval is None
    pair['close'] = 1.0009
    assert buystrat.evaluate(pair, indicators) is None
    pair['close'] = 1.001
    print(buystrat.evaluate(pair, indicators))
    assert not buystrat.evaluate(pair, indicators) is None
    pair['close'] = 1.00
    indicators['MFI_30m'] = 0
    print(buystrat.evaluate(pair, indicators))
    assert buystrat.evaluate(pair, indicators) is None
    assert not 'ADA/ETH' in buystrat.pairs_trailing

def test_dcabuy_strategy():
    pair = pair1.copy()
    indicators = indicators1.copy()
    buystrat = DCABuyCondition(strategy)
    eval = buystrat.evaluate(pair, indicators)
    assert not 'ADA/ETH' in buystrat.pairs_trailing
    assert eval is None
    pair['close'] = 0.95
    assert buystrat.evaluate(pair, indicators) is None
    pair['close'] = 0.955
    print(buystrat.evaluate(pair, indicators))
    assert not buystrat.evaluate(pair, indicators) is None
    pair['close'] = 1.00
    indicators['MFI_30m'] = 0
    print(buystrat.evaluate(pair, indicators))
    assert buystrat.evaluate(pair, indicators) is None
    assert not 'ADA/ETH' in buystrat.pairs_trailing

def test_sell_strategy():
    pair = pair1.copy()
    indicators = indicators1.copy()
    sellstrat = SellCondition(strategy)
    eval = sellstrat.evaluate(pair, indicators)
    assert not 'ADA/ETH' in sellstrat.pairs_trailing
    assert eval is None
    pair['close'] = 1
    assert sellstrat.evaluate(pair, indicators) is None
    pair['close'] = 1.02
    print(sellstrat.evaluate(pair, indicators))
    pair['close'] = 1.015
    print(sellstrat.evaluate(pair, indicators))
    assert sellstrat.evaluate(pair, indicators) == 1.01
    pair['close'] = 1.00
    indicators['MFI_30m'] = 0
    print(sellstrat.evaluate(pair, indicators))
    assert sellstrat.evaluate(pair, indicators) is None
    assert not 'ADA/ETH' in sellstrat.pairs_trailing

if __name__ == '__main__':
    pytest.main()