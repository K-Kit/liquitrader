import sys
sys.path.append('..')

import pytest
import pandas.core.frame

from exchanges import Binance
from analyzers.TechnicalAnalysis import run_ta

# test keys, trading disabled
from dev_keys_binance import keys


ex = Binance.BinanceExchange('binance', {'public': keys.public, 'secret': keys.secret})
# use USDT in tests to decrease API calls (only ~12 pairs vs 100+)
timeframes=['5m']
ex.start(market='USDT', timeframes=timeframes)

indicators = {
        'MFI': {'name': 'MFI', 'candle_period': 0, 'lookback': [1,2,3,4]},
        'BBANDS': {'name': 'BBANDS', 'candle_period': 0, 'lookback': None},

    }

pairs = ex.pairs
for pair in pairs:
    pairs[pair]['indicators'] = run_ta(pairs[pair]['candlesticks'], indicators)

from pprint import pprint

indicators = pairs['ADA/USDT']['indicators']

def test_current_is_last_in_array():
    # test to make sure upperband_5m is most current value in upperband_5m array
    assert indicators['UPPERBAND_5m'] == indicators['UPPERBAND_ARRAY_5m'][-1]


def test_change_over_n():
    # change over n = array[-1] - array[-1-n]
    array = indicators['MFI_ARRAY_5m']
    assert indicators['MFI_CHANGE_OVER_3_5m'] == array[-1] - array[-4]

if __name__ == '__main__':
    pytest.main()