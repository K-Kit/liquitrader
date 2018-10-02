import pickle
import talib as ta
from talib import abstract
import pandas as pd
from talib.abstract import *

import sys
import numpy as np
ta_list = ta.get_functions()

def get_output_for_indicator(indicator):
    '''
    get outputs for ta-indicator
    :param key:
    :return: Output value name(s)
    '''
    info = Function(indicator).info
    outs = list(map(str.upper, info['output_names']))
    if len(outs) == 1:
        return [indicator]
    return outs


def get_inputs(df):
    df = df.astype(float)
    o, h, l, c, v = df['open'].values * 100000000, df['high'].values * 100000000, df['low'].values* 100000000, df['close'].values * 100000000, df['volume'].values * 100000000
    # o, h, l, c, v = df['o'].values, df['h'].values, df['l'].values, df[
    #     'c'].values, df['v'].values
    inputs = {
        'open': o,
        'high': h,
        'low': l,
        'close': c,
        'volume': v
    }
    return inputs


def append_candle_period(candle_period, indicator):
    if candle_period == 0:
        return indicator
    return '{}_{}'.format(indicator, candle_period)


def get_indicators(df, indicator_name, candle_period=0):
    indicator_name = indicator_name.upper()
    inputs = get_inputs(df)
    output_names = get_output_for_indicator(indicator_name)
    outputs = [append_candle_period(candle_period, item) for item in output_names]
    indicator_calculation = abstract.Function(indicator_name)
    if Function(indicator_name).info['function_flags'] is None:
        is_price = False
    else:
        is_price = 'Output scale same as input' in Function(indicator_name).info['function_flags']\
                   or 'MACD' in indicator_name


    if candle_period > 0:
        res = indicator_calculation(inputs, timeperiod=candle_period)
    else:
        res = indicator_calculation(inputs)

    if is_price:
        if type(res) == list:
            for part in res:
                part /= 100000000

        else:
            res /= 100000000

    i = 0
    if not isinstance(res,list):
        res = [res]
    return list(zip(outputs,res))



def run_ta(candlesticks, indicators):
    '''
    Runs calculation for each indicator and sets the value
    in the Pair attributes
    this is called every time the websocket tics
    :param pair:
    '''
    stats = {}
    for key in candlesticks:
        for k, indicator in indicators.items():
            if indicator['name'] in ta_list:
                inds = get_indicators(candlesticks[key], indicator['name'],candle_period= indicator['candle_period'])
                for k, v in inds:
                    stats.update({k + '_'+key: v})



    return stats


if __name__ == '__main__':
    with open('../pairs_data.pcl', 'rb') as f:
        pairs = pickle.load(f)


    indicators = {
        'MFI': {'name': 'MFI', 'candle_period': 24},
        'BBANDS': {'name': 'BBANDS', 'candle_period': 32},

    }

    # for pair in pairs:
    #     pairs[pair]['indicators'] = run_ta(pairs[pair]['candlesticks'], indicators)

    from pprint import pprint

    z = run_ta(pairs['ADA/USDT']['candlesticks'], indicators)
    print(z.keys())
    # print(z['MFI_ARRAY_5m'])
    # print(type(z['MFI_ARRAY_5m']))

    # print(pairs['ADA/USDT']['indicators'].keys())

