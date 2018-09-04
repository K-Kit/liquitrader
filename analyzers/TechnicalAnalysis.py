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


def join_key_value(key, value):
    return {key: value[-1]}


def handle_indicators(outputs, *args):
    if len(outputs) == 1:
        return (list(map(join_key_value, outputs, args)))
    else:
        return (list(map(join_key_value, outputs, *args)))


def calculate_indicator_change(array, change_period, asPercent = False):
    try:
        if asPercent:
            return (array[-1] - array[-1 - change_period]) / array[-1 - change_period] * 100
        else:
            return array[-1] - array[-1 - change_period]
    except Exception as ex:
        # logger.critical(ex)
        return np.nan

def calculate_lookback(array, change_period):
    try:

        return array[-1 - change_period]
    except Exception as ex:
        # logger.critical(ex)
        return np.nan


class Output():
    value = np.nan
    array = np.ndarray
    precision = 8

    def __init__(self, name):
        self.name = name


def get_indicators(df, indicator_name, lookback=None, candle_period=0):
    if lookback is None:
        lookback = [1]
    indicator_name = indicator_name.upper()
    inputs = get_inputs(df)
    output_names = get_output_for_indicator(indicator_name)
    outputs = [Output(append_candle_period(candle_period, item)) for item in output_names]
    indicator_calculation = abstract.Function(indicator_name)
    if Function(indicator_name).info['function_flags'] is None:
        is_price = False
    else:
        is_price = 'Output scale same as input' in Function(indicator_name).info['function_flags']



    if 'MACD' in indicator_name:
        precision = 8
        is_price = True
    elif is_price:
        precision = 8
    # elif indicator_name[:3] == 'CDL':
    #     precision = 'bool'
    else:
        precision = 0

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

    i=0
    if len(outputs) > 1:
        for i in range(len(outputs)):
            outputs[i].array = res[i]
            try:
                outputs[i].__setattr__('{}'.format(outputs[i].name), res[i][-1])
            except Exception as ex:
                outputs[i].__setattr__('{}'.format(outputs[i].name),
                                       np.nan)
            outputs[i].__setattr__('{}_ARRAY'.format(outputs[i].name), res[i])
            i+=1

    else:
        outputs[0].array = res
        try:
            outputs[0].__setattr__('{}'.format(outputs[0].name), res[-1])
        except Exception as ex:
            # logger.debug('TA: P{}'.format(ex))
            outputs[0].__setattr__('{}'.format(outputs[0].name),
                                   np.nan)
        outputs[0].__setattr__('{}_ARRAY'.format(outputs[0].name), res )



    for period in lookback:
        if len(outputs) > 1:
            for i in range(len(outputs)):
                if i == 0:
                    outputs[i].__setattr__('{}_CHANGE'.format(outputs[i].name),
                                           calculate_indicator_change(outputs[i].array, 1, is_price))
                outputs[i].__setattr__('{}_CHANGE_OVER_{}'.format(outputs[i].name, period),
                                       calculate_indicator_change(outputs[i].array, period, is_price))

                outputs[i].__setattr__('{}_LOOKBACK_{}'.format(outputs[i].name, period),
                                       calculate_lookback(outputs[i].array, period))
                i += 1
        else:
            outputs[0].__setattr__('{}_CHANGE_OVER_{}'.format(outputs[0].name, period),
                                   calculate_indicator_change(outputs[0].array, period, is_price))

            outputs[0].__setattr__('{}_LOOKBACK_{}'.format(outputs[0].name, period),
                                   calculate_lookback(outputs[0].array, period))

            outputs[0].__setattr__('{}_CHANGE'.format(outputs[0].name, period),
                                   calculate_indicator_change(outputs[0].array, period, is_price))


    if len(outputs) > 1:
        for output in outputs:
            delattr(output, 'name')
            delattr(output, 'array')
        return list(map(vars,outputs))
    else:
        delattr(outputs[0], 'name')
        delattr(outputs[0], 'array')
        return vars(outputs[0])


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
                inds = get_indicators(candlesticks[key], indicator['name'],candle_period= indicator['candle_period'], lookback=indicator['lookback'])
                try:
                    if type(inds) == list:
                        for item in inds:
                            for ind, value in item.items():
                                stats['{}_{}'.format(ind, key)] = value


                    else:
                        for ind, value in inds.items():
                            stats['{}_{}'.format(ind, key)] = value

                except Exception as ex:
                    pass
    return stats


if __name__ == '__main__':
    with open('../pairs_data.pcl', 'rb') as f:
        pairs = pickle.load(f)


    indicators = {
        'MFI': {'name': 'MFI', 'candle_period': 0, 'lookback': None},
        'BBANDS': {'name': 'BBANDS', 'candle_period': 0, 'lookback': None},

    }

    for pair in pairs:
        pairs[pair]['indicators'] = run_ta(pairs[pair]['candlesticks'], indicators)

    from pprint import pprint

    # pprint(run_ta(pairs['ADA/USDT']['candlesticks'], indicators))
    print(pairs['ADA/USDT']['indicators'].keys())

