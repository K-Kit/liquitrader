from bearpuncher import *

from flask import Flask
from flask import jsonify

app = Flask(__name__)

global BP_ENGINE
BP_ENGINE = None

@app.route("/")
def gethello():
    return "hello"


@app.route("/holding")
def get_holding():
    df = BP_ENGINE.pairs_to_df(friendly=True)
    df[df['Amount'] > 0].to_json(orient='records', path_or_buf='holding')
    return jsonify(df[df['Amount'] > 0].to_json(orient='records'))


@app.route("/market")
def get_market():
    df = BP_ENGINE.pairs_to_df(friendly=True)
    df[FRIENDLY_MARKET_COLUMNS].to_json(orient='records', path_or_buf='market')

    return jsonify(df[FRIENDLY_MARKET_COLUMNS].to_json(orient='records'))


@app.route("/buy_log")
def get_buy_log_frame():
    df = pd.DataFrame(BP_ENGINE.trade_history)
    df['gain'] = (df.price - df.bought_price) / df.bought_price * 100
    df['net_gain'] = (df.price - df.bought_price) * df.filled
    cols = ['datetime', 'symbol', 'bought_price', 'price', 'amount', 'side', 'status', 'remaining', 'filled', 'gain']
    df[df.side == 'buy'][cols].to_json(orient='records', path_or_buf='buy_log')

    return jsonify(df[df.side == 'buy'][cols].to_json(orient='records'))


@app.route("/sell_log")
def get_sell_log_frame():
    df = pd.DataFrame(BP_ENGINE.trade_history)
    df['gain'] = (df.price - df.bought_price) / df.bought_price * 100
    cols = ['datetime', 'symbol', 'bought_price', 'price', 'amount', 'side', 'status', 'remaining', 'filled', 'gain']
    df[df.side == 'sell'][cols].to_json(orient='records', path_or_buf='sell_log')
    return jsonify(df[df.side == 'sell'][cols].to_json(orient='records'))


@app.route("/dashboard_data")
def get_dashboard_data():
    data = {
        "quote_balance": BP_ENGINE.exchange.balance,
        "total_pending_value": BP_ENGINE.get_pending_value(),
        "total_current_value": BP_ENGINE.get_tcv(),
        "total_profit": BP_ENGINE.get_total_profit(),
        "total_profit_percent": BP_ENGINE.get_total_profit() / BP_ENGINE.exchange.balance * 100,
        "daily_profit_data": BP_ENGINE.get_daily_profit_data().to_json(orient='records'),
        "holding_chart_data": BP_ENGINE.pairs_to_df()['total_cost'].dropna().to_json(orient='records'),
        "cum_profit": BP_ENGINE.get_cumulative_profit().to_json(orient='records'),
        "pair_profit_data": BP_ENGINE.get_pair_profit_data().to_json(orient='records')
    }

    return data
