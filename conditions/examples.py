mfi_30_change_3_5m = {'value': 'MFI', 'change_over': 3, 'candle_period': 30, 'timeframe': '5m'}
mfi_30_15m = {'value': 'MFI', 'candle_period': "30", 'timeframe': '15m'}
mfi_30m = {'value': 'MFI', 'timeframe': '30m'}
lowerband_5m = {'value': 'lowerband', 'timeframe': '5m'}
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
pair1 = {'symbol': 'ADA/ETH', 'close': 5, 'quoteVolume': 1000, 'bought_value': 1, 'current_value': 1.0}
