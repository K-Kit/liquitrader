from bearpuncher import *

import flask
from flask import jsonify, request
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)

global BP_ENGINE
BP_ENGINE = None

@app.route("/")
def gethello():
    return "hello"


@app.route("/holding")
def get_holding():
    df = BP_ENGINE.pairs_to_df(friendly=True)
    if 'Amount' not in df:
        return '[]'
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
    if 'price' not in df:
        return '[]'
    cols = ['datetime', 'symbol', 'price', 'amount', 'side', 'status', 'remaining', 'filled']
    df[df.side == 'buy'][cols].to_json(orient='records', path_or_buf='buy_log')

    return jsonify(df[df.side == 'buy'][cols].to_json(orient='records'))


@app.route("/sell_log")
def get_sell_log_frame():
    df = pd.DataFrame(BP_ENGINE.trade_history)
    if 'price' not in df:
        return '[]'
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


@app.route('/update_config', methods=['POST'])
def update_config():
    data = request.data.decode()
    # data
    BP_ENGINE.config.update_config(data['section'], data['data'])
    return data


@app.route("/config")
def get_config():
    cfg = vars(BP_ENGINE.config)
    return jsonify(str(cfg))



if __name__ == '__main__':
    import bearpuncher
    BP_ENGINE = bearpuncher.Bearpuncher()
    BP_ENGINE.initialize_config()
    app.run('0.0.0.0', 80, debug=True)