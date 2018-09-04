import pytest
import sys
sys.path.append('..')
from exchanges import Binance

class keys:
    public = 'HPTpbOKj0konuPW72JozWGFDJbo0nK2rymbyObeX1vDSDSMZZd6vVosrA9dPFa1L'
    secret = '4AuwPy6mVarrUqqECbyZSU9GrfOrInt6MIHdqvxHZWMaCXEjbSGGjBEuKmpCwPtb'


ex = Binance.BinanceExchange('binance', {'public': keys.public, 'secret': keys.secret})
ex.start(market='ETH')

def test_market():
    assert 'ADA/ETH' in ex.pairs
