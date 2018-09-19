import sys
sys.path.append('..')

import pytest
import pandas.core.frame

from exchanges import Binance

# test keys, trading disabled
class keys:
    public = 'HPTpbOKj0konuPW72JozWGFDJbo0nK2rymbyObeX1vDSDSMZZd6vVosrA9dPFa1L'
    secret = '4AuwPy6mVarrUqqECbyZSU9GrfOrInt6MIHdqvxHZWMaCXEjbSGGjBEuKmpCwPtb'

timeframes=['5m', '15m', '30m']
ex = Binance.BinanceExchange('binance','USDT' , {'public': keys.public, 'secret': keys.secret},timeframes)
# use USDT in tests to decrease API calls (only ~12 pairs vs 100+)
ex.initialize()

def test_market():
    assert 'ADA/USDT' in ex.pairs

# TODO come up with new balance tests, old ones dont work right now will have to add defaults for no balance or something
# def test_balances():
#     assert 'ADA/ETH' in ex.wallet
#     assert isinstance(ex.balances['ADA/ETH'], dict)
#     assert 'free' in ex.balances['ADA/ETH']

def test_candles_not_none():
    # test to make sure candles aren't null
    # test to make sure candles are dataframe
    ada_5m_candles = ex.pairs['ADA/USDT']['candlesticks']['5m']
    assert len(ada_5m_candles) > 10, 'populate candles did not fetch full candle history'
    assert isinstance(ada_5m_candles,pandas.core.frame.DataFrame), 'candle history did not get converted to dataframe'

def test_all_timeperiods_added():
    ada_candles = ex.pairs['ADA/USDT']['candlesticks']
    assert list(ada_candles.keys()) == timeframes, 'did not fetch all timeframes'
    for t in timeframes:
        assert isinstance(ada_candles[t],pandas.core.frame.DataFrame), 'candle history did not get converted to dataframe'
        assert len(ada_candles[t]) > 10, 'populate candles did not fetch full candle history'

def test_all_pairs_have_candles():
    # test to make sure all pairs have candlestick data
    for pair in ex.pairs:
        candle_5m = ex.pairs[pair]['candlesticks']['5m']
        assert isinstance(candle_5m,pandas.core.frame.DataFrame)
        assert len(candle_5m) > 10, 'populate candles did not fetch full candle history or pair is new: {}'.format(pair)

def test_eth_not_in_usdt():
    # test to make sure we only get USDT pairs when fetching USDT
    assert 'ADA/ETH' not in ex.pairs

def test_orderbook():
    # test to make sure orderbook is float and in form [price, amount]
    second_bid = ex.pairs['ADA/USDT']['bids'][2]
    # if its a price it will be less than 2 this could change if the price of ADA goes up 200x
    assert second_bid[0] < 2, 'price amount order wrong or price of ADA exceeded $2'
    # the amount will almost always be > 5, there could be exceptions but extremely unlikely
    assert second_bid[1] > 5, 'price amount order wrong or extremely thin orderbook'
    assert isinstance(second_bid[0], float), 'orderbook float conversion err'



if __name__ == '__main__':
    pytest.main()