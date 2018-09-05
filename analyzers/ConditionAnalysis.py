"""
This will take in a list of conditions
"""
import operator as py_operators


import json
filename = '../config/config.json'
with open(filename, 'r') as f:
    config = json.load(f)

from pprint import pprint
bs = config['general']['buy_strategies']
# pprint(bs)

b = bs[0]
indicators = {'MFI_5m': 30, "MA_5m": 1, 'MFI_ARRAY_5m': [1,2,3,4,5], "MA_ARRAY_5m": [1,2,3,4,5]}
op_translate = {'<': py_operators.lt, '<=': py_operators.le,
                '>': py_operators.gt, '>=': py_operators.ge,
                '=': py_operators.eq, '==': py_operators.eq}

def float_or_price(part, price):
    return price if part.lower() == 'price' else float(part)

def get_parts(parts, indicators, price):
    a = indicators[parts[0]] if parts[0] in indicators else float_or_price(parts[0], price)
    b = indicators[parts[2]] if parts[2] in indicators else float_or_price(parts[2], price)
    return a, b, parts[1].lower()

def part_to_list_reversed(part, period):
    return list(reversed(part)) if not isinstance(part, float) and not isinstance(part, int) else [part]* (period + 1)

def handle_cross_condition(part_a,part_b,op):
    try:
        period = int(op.rsplit('_',1)[1])
    except ValueError:
        period = 1

    a = part_to_list_reversed(part_a, period)
    b = part_to_list_reversed(part_b, period)
    if 'cross_up' in op:
        res = a[0] - b[0] > 0 and a[period] - b[period] < 0

    elif 'cross_down' in op:
        res = a[0] - b[0] < 0 and a[period] - b[period] > 0

    else:
        return False
    return res



def evaluate_conditions(conditions: list, indicators: dict, price: float, bought_price = None):
    """
    Loop through list of conditions, evaluate all conditions vs indicators dict or price.
    If this is a standard comparison, use op translate.
    Else if cross condition, get corresponding arrays to evaluate cross condition.
    Add conditions to results dict.
    :param conditions:
    :param indicators:
    :param price:
    :return: results(dict {condition: bool})
    """
    results = {}
    for condition in conditions:
        parts = condition.split()

        # handle standard op condition
        if len(parts) == 3 and parts[1] in op_translate:
            a,b,op = get_parts(parts, indicators, price)
            results[condition] = op_translate[op](a, b)

        elif len(parts) == 3 and 'cross' in parts[1].lower():

            a = indicators['{}_ARRAY_{}'.format(*parts[0].rsplit('_', 1))] if parts[0] in indicators \
                else float_or_price(parts[0], price)

            b = indicators['{}_ARRAY_{}'.format(*parts[2].rsplit('_', 1))] if parts[2] in indicators \
                else float_or_price(parts[2], price)

            op = parts[1].lower()

            results[condition] = handle_cross_condition(a,b,op)

    return results

if __name__ == '__main__':
    conditions = b['conditions'][0].split(',')
    cons2 = []
    cons2.append('MFI_5m cross_up 3')
    cons2.append('MFI_5m cross_up price')
    res = evaluate_conditions(conditions, indicators, 3)
    val = handle_cross_condition([1, 2, 3], 2, 'cross_up_2')
    val2 = handle_cross_condition([3, 2, 1], 2, 'cross_down_2')
    print(res)