from liquitrader import *

import flask
from flask import jsonify

app = flask.Flask(__name__)

LT_TRADER = None


def run(shutdown_handler):
    shutdown_handler.add_task()
    app.run('0.0.0.0', 80)


def stop(shutdown_handler):
    app_stop_func = flask.request.environ.get('werkzeug.server.shutdown')

    if app_stop_func is not None:
        app_stop_func()
    else:
        print('Failed to shutdown GUI')

    shutdown_handler.remove_task()


@app.route("/")
def gethello():
    return "hello"


@app.route("/holding")
def get_holding():
    df = LT_TRADER.pairs_to_df(friendly=True)
    df[df['Amount'] > 0].to_json(orient='records', path_or_buf='holding')
    return jsonify(df[df['Amount'] > 0].to_json(orient='records'))


@app.route("/market")
def get_market():
    df = LT_TRADER.pairs_to_df(friendly=True)
    df[FRIENDLY_MARKET_COLUMNS].to_json(orient='records', path_or_buf='market')

    return jsonify(df[FRIENDLY_MARKET_COLUMNS].to_json(orient='records'))


@app.route("/buy_log")
def get_buy_log_frame():
    df = pd.DataFrame(LT_TRADER.trade_history)
    df['gain'] = (df.price - df.bought_price) / df.bought_price * 100
    df['net_gain'] = (df.price - df.bought_price) * df.filled
    cols = ['datetime', 'symbol', 'bought_price', 'price', 'amount', 'side', 'status', 'remaining', 'filled', 'gain']
    df[df.side == 'buy'][cols].to_json(orient='records', path_or_buf='buy_log')

    return jsonify(df[df.side == 'buy'][cols].to_json(orient='records'))


@app.route("/sell_log")
def get_sell_log_frame():
    df = pd.DataFrame(LT_TRADER.trade_history)
    df['gain'] = (df.price - df.bought_price) / df.bought_price * 100
    cols = ['datetime', 'symbol', 'bought_price', 'price', 'amount', 'side', 'status', 'remaining', 'filled', 'gain']
    df[df.side == 'sell'][cols].to_json(orient='records', path_or_buf='sell_log')
    return jsonify(df[df.side == 'sell'][cols].to_json(orient='records'))


@app.route("/dashboard_data")
def get_dashboard_data():
    data = {
        "quote_balance": LT_TRADER.exchange.balance,
        "total_pending_value": LT_TRADER.get_pending_value(),
        "total_current_value": LT_TRADER.get_tcv(),
        "total_profit": LT_TRADER.get_total_profit(),
        "total_profit_percent": LT_TRADER.get_total_profit() / LT_TRADER.exchange.balance * 100,
        "daily_profit_data": LT_TRADER.get_daily_profit_data().to_json(orient='records'),
        "holding_chart_data": LT_TRADER.pairs_to_df()['total_cost'].dropna().to_json(orient='records'),
        "cum_profit": LT_TRADER.get_cumulative_profit().to_json(orient='records'),
        "pair_profit_data": LT_TRADER.get_pair_profit_data().to_json(orient='records')
    }

    return data
