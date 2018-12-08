import talib as ta
from talib import abstract
import pandas as pd

from talib.abstract import *
import operator as py_operators
import numpy

import traceback
# a op b
PATTERNS = [
    "CDL2CROWS",
    "CDL3BLACKCROWS",
    "CDL3INSIDE",
    "CDL3LINESTRIKE",
    "CDL3OUTSIDE",
    "CDL3STARSINSOUTH",
    "CDL3WHITESOLDIERS",
    "CDLABANDONEDBABY",
    "CDLADVANCEBLOCK",
    "CDLBELTHOLD",
    "CDLBREAKAWAY",
    "CDLCLOSINGMARUBOZU",
    "CDLCONCEALBABYSWALL",
    "CDLCOUNTERATTACK",
    "CDLDARKCLOUDCOVER",
    "CDLDOJI",
    "CDLDOJISTAR",
    "CDLDRAGONFLYDOJI",
    "CDLENGULFING",
    "CDLEVENINGDOJISTAR",
    "CDLEVENINGSTAR",
    "CDLGAPSIDESIDEWHITE",
    "CDLGRAVESTONEDOJI",
    "CDLHAMMER",
    "CDLHANGINGMAN",
    "CDLHARAMI",
    "CDLHARAMICROSS",
    "CDLHIGHWAVE",
    "CDLHIKKAKE",
    "CDLHIKKAKEMOD",
    "CDLHOMINGPIGEON",
    "CDLIDENTICAL3CROWS",
    "CDLINNECK",
    "CDLINVERTEDHAMMER",
    "CDLKICKING",
    "CDLKICKINGBYLENGTH",
    "CDLLADDERBOTTOM",
    "CDLLONGLEGGEDDOJI",
    "CDLLONGLINE",
    "CDLMARUBOZU",
    "CDLMATCHINGLOW",
    "CDLMATHOLD",
    "CDLMORNINGDOJISTAR",
    "CDLMORNINGSTAR",
    "CDLONNECK",
    "CDLPIERCING",
    "CDLRICKSHAWMAN",
    "CDLRISEFALL3METHODS",
    "CDLSEPARATINGLINES",
    "CDLSHOOTINGSTAR",
    "CDLSHORTLINE",
    "CDLSPINNINGTOP",
    "CDLSTALLEDPATTERN",
    "CDLSTICKSANDWICH",
    "CDLTAKURI",
    "CDLTASUKIGAP",
    "CDLTHRUSTING",
    "CDLTRISTAR",
    "CDLUNIQUE3RIVER",
    "CDLUPSIDEGAP2CROWS",
    "CDLXSIDEGAP3METHODS",
]
# note change over will no longer be usable in cross
talib_indicators = ta.get_functions()
op_translate = {'<': py_operators.lt, '<=': py_operators.le,
                '>': py_operators.gt, '>=': py_operators.ge,
                '=': py_operators.eq, '==': py_operators.eq}


# this function is used to calculate how much of a token to buy, if the user is using a percent value, calculate
# the percentage of balance, otherwise use static value in quote currency
def get_buy_value(x, total_balance):
    if isinstance(x, str):
        return total_balance * percentToFloat(x)
    else:
        return x


def percentToFloat(x):
    return float(x.strip('%')) / 100


def calculate_indicator_change(array, change_period, asPercent=False):
    try:
        change_period = int(change_period)
    except ValueError:
        return None
    try:
        if asPercent:
            return (array[-1] - array[-1 - change_period]) / array[-1 - change_period] * 100
        else:
            return array[-1] - array[-1 - change_period]
    except Exception as ex:
        print(array, change_period)
        print('calculate indicator change line 37: {}'.format(traceback.format_exc()))
        return None


def isPriceLike(indicator_name):
    if Function(indicator_name).info['function_flags'] is None:
        return False
    elif 'MACD' in indicator_name:
        return True
    else:
        return 'Output scale same as input' in Function(indicator_name).info['function_flags']


def ind_dict_to_full_name(indicator: dict):
    if 'candle_period' in indicator and indicator['candle_period'] != '':
        return "_".join([indicator['value'], str(indicator['candle_period']), indicator['timeframe']])
    else:
        return "_".join([indicator['value'], indicator['timeframe']])


def translate(operand: dict, inputs):
    # if the value is a talib indicators, its full name
    if operand['value'] in talib_indicators or operand['value'] in PATTERNS:
        indicator = ind_dict_to_full_name(operand)
        if indicator not in inputs:
            if indicator.replace('__', '_') in inputs:
                indicator = indicator.replace('__', '_')
            else:
                return None
        if 'change_over' in operand and operand['change_over'] != "":
            return calculate_indicator_change(inputs[indicator], operand['change_over'], isPriceLike(operand['value']))
        else:
            return inputs[indicator]
    elif operand['value'] == 'price':
        return inputs['close']

    elif operand['value'] == 'volume':
        return inputs['quoteVolume']

    elif type(operand['value']) == int or type(operand['value']) == float:
        return operand['value']

    elif '%' in operand['value']:
        return percentToFloat(operand['value'])
    else:
        try:
            return float(operand['value'])
        except Exception as ex:
            print('condition analyzer 143: ', ex, operand)
            return None


# get the value for the indicator, if its a list or numpy array get last element, if its static return the value
def getCurrentValue(val, inputs):
    value = translate(val, inputs)
    if value is None: return None
    if isinstance(value, numpy.ndarray) or isinstance(value, list):
        return value[len(value) - 1]
    else:
        return value


def getLookback(val, inputs , cross_candles):
    val = translate(val,inputs)
    try:
        return val[len(val) - 1 - cross_candles]
    except Exception as ex:
        return val


def handle_cross_condition(part_a, part_b, op, inputs, cross_candles=1):
    a1 = getCurrentValue(part_a,inputs)
    a2 = getLookback(part_a, inputs, cross_candles)

    b1 = getCurrentValue(part_b, inputs)
    b2 = getLookback(part_b, inputs, cross_candles)
    if 'cross_up' in op:
        return a1 - b1 >= 0 and a2 - b2 <= 0

    elif 'cross_down' in op:
        return a1 - b1 <= 0 and a2 - b2 >= 0

    else:
        return False


# ----
def handle_gain_strat(pair, part, is_buy):
    """
    if buy return price > (indicator)*(1+n/100)
    if sell return price < (indicator)*(1+n/100)
    :param pair:
    :param part:
    :param is_buy:
    :return:
    """
    indicator_value = get_val(pair, part[0])
    gain_value = 1 + (get_val(pair, part[2]) / 100)

    scaled_value = indicator_value * gain_value

    if is_buy:
        return pair.price <= scaled_value

    else:
        return pair.price >= scaled_value


failcounter=0

# TODO GAIN and other strats
def evaluate_condition(cond, pair, indicators, is_buy = True):
    global failcounter
    inputs = {**pair, **indicators}
    if cond['left']['value'] in PATTERNS:
        a = getCurrentValue(cond['left'], inputs)
        if a is None:
            print(cond, indicators.keys())
            return False
        if 'inverse' in cond and cond['inverse']:
            return a < 0
        else:
            return a > 0
    elif cond['op'] in op_translate:
        a = getCurrentValue(cond['left'], inputs)
        b = getCurrentValue(cond['right'], inputs)
        if a is None or b is None:
            return False
        res = op_translate[cond['op']](a, b)
        return res
    elif 'cross' in cond['op']:
        return handle_cross_condition(cond['left'], cond['right'], cond['op'], inputs, cond['cross_candles'])
    elif cond['op'] == 'gain':
        indicator_value = getCurrentValue(cond['left'], inputs)
        gain_value = getCurrentValue(cond['right'], inputs)
        scaled_value = indicator_value * gain_value

        if is_buy:
            return pair.price <= scaled_value
        else:
            return pair.price >= scaled_value

    elif cond['op'] == 'min_volume':
        return float(pair['quoteVolume']) >= cond['right']
    elif cond['op'] == 'min_profit':
        return (pair['current_value'] - pair['total_cost'])/pair['total_cost']*100 >= cond['right']
    


# if __name__ == '__main__':
#     # test operands
#     from examples import *
#
#     print(evaluate_condition(condition_1, pair1, indicators1))
#     print(evaluate_condition(condition_2, pair1, indicators1))
#     print(evaluate_condition(condition_3, pair1, indicators1))
#     print(evaluate_condition(condition_4, pair1, indicators1))
#     print(evaluate_condition(condition_5, pair1, indicators1))
#     print(evaluate_condition(condition_6, pair1, indicators1))

