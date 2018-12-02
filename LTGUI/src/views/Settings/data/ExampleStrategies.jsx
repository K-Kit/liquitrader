export const exampleBuyStrategies = [
    {
        "conditions": [
            {"left": {"value": "MFI", "timeframe": "30m"}, "op": "<", "right": {"value": 40}},
            {"left": {"value": "MFI", "change_over": 2, "candle_period": 30, "timeframe": "5m"}, "op": ">", "right": {"value": 1}},
            {"left": {"value": "MFI", "timeframe": "1h"}, "op": "<", "right": {"value": 50}}

        ],
        "buy_value": "2%",
        "trailing %": 0.00,
        "min_price": 0,
        "min_volume": 0
    },
    {
        "conditions": [
            {"left": {"value": "RSI", "timeframe": "30m"}, "op": "<", "right": {"value": 10}},
            {"left": {"value": "MFI", "change_over": 2, "candle_period": 30, "timeframe": "5m"}, "op": ">", "right": {"value": 1}},
            {"left": {"value": "MFI", "timeframe": "1h"}, "op": "<", "right": {"value": 50}}

        ],
        "buy_value": "2%",
        "trailing %": 0.3,
        "min_price": 30,
        "min_volume": 1220
    }
];

export const exampleDCAStrategies = [
    {
        "conditions": [
            {"left": {"value": "MFI", "timeframe": "30m"}, "op": "<", "right": {"value": 40}},
            {"left": {"value": "MFI", "change_over": 2, "candle_period": 30, "timeframe": "5m"}, "op": ">", "right": {"value": 1}},
            {"left": {"value": "MFI", "timeframe": "1h"}, "op": "<", "right": {"value": 50}}
        ],
        "max_dca_level": 4,
        "trailing %": 0.3,
        "dca_strategy": {
            "default": {"trigger": -3.5, "percentage": 50},
            "1": {"trigger": -7.5, "percentage": 200},
            "0": {"trigger": -1, "percentage": 50}
        }
    }
];