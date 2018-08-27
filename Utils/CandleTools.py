import pandas as pd

def candles_to_df(candle_list):
    return pd.DataFrame(candle_list, dtype=float, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])