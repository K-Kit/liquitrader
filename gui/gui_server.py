from liquitrader import *

import flask
from flask import jsonify
from flask_cors import CORS

import requests

app = flask.Flask(__name__)

LT_ENGINE = None


def run(shutdown_handler):
    shutdown_handler.add_task()
    app.run('0.0.0.0', 80)


def stop(shutdown_handler):
    # TODO: SHUTDOWN CHEROOT HERE
    _ = requests.get('http://localhost/shutdown')
    shutdown_handler.remove_task()


@app.route("/shutdown", methods=['GET'])
def shutdown():
    # TODO: This only works for Flask
    app_stop_func = flask.request.environ.get('werkzeug.server.shutdown')

    if app_stop_func is not None:
        app_stop_func()
        return flask.Response(status=200)

    else:
        print('Failed to shutdown GUI')
        return flask.Response(status=500)


app = flask.Flask(__name__)
CORS(app)


@app.route("/")
def gethello():
    return "hello"


@app.route("/holding")
def get_holding():
    df = LT_ENGINE.pairs_to_df(friendly=True)

    if 'Amount' not in df:
        return jsonify([])

    df[df['Amount'] > 0].to_json(orient='records', path_or_buf='holding')
    return jsonify(df[df['Amount'] > 0].to_json(orient='records'))


@app.route("/market")
def get_market():
    df = LT_ENGINE.pairs_to_df(friendly=True)
    df[FRIENDLY_MARKET_COLUMNS].to_json(orient='records', path_or_buf='market')

    return jsonify(df[FRIENDLY_MARKET_COLUMNS].to_json(orient='records'))


@app.route("/buy_log")
def get_buy_log_frame():
    df = pd.DataFrame(LT_ENGINE.trade_history)
    if 'price' not in df:
        return jsonify([])

    cols = ['datetime', 'symbol', 'price', 'amount', 'side', 'status', 'remaining', 'filled']


    return jsonify(df[df.side == 'buy'][cols].to_json(orient='records'))


@app.route("/sell_log")
def get_sell_log_frame():
    df = pd.DataFrame(LT_ENGINE.trade_history)

    if 'bought_price' not in df:
        return jsonify([])

    df['gain'] = (df.price - df.bought_price) / df.bought_price * 100
    cols = ['datetime', 'symbol', 'bought_price', 'price', 'amount', 'side', 'status', 'remaining', 'filled', 'gain']

    return jsonify(df[df.side == 'sell'][cols].to_json(orient='records'))


@app.route("/dashboard_data")
def get_dashboard_data():
    data = {
        "quote_balance": LT_ENGINE.exchange.balance,
        "total_pending_value": LT_ENGINE.get_pending_value(),
        "total_current_value": LT_ENGINE.get_tcv(),
        "total_profit": LT_ENGINE.get_total_profit(),
        "total_profit_percent": LT_ENGINE.get_total_profit() / LT_ENGINE.exchange.balance * 100,
        "daily_profit_data": LT_ENGINE.get_daily_profit_data().to_json(orient='records'),
        "holding_chart_data": LT_ENGINE.pairs_to_df()['total_cost'].dropna().to_json(orient='records'),
        "cum_profit": LT_ENGINE.get_cumulative_profit().to_json(orient='records'),
        "pair_profit_data": LT_ENGINE.get_pair_profit_data().to_json(orient='records')
    }

    return data


@app.route('/update_config', methods=['POST'])
def update_config():
    data = flask.request.data.decode()
    LT_ENGINE.config.update_config(data['section'], data['data'])

    return data


@app.route("/config")
def get_config():
    return jsonify(str(vars(LT_ENGINE.config)))
