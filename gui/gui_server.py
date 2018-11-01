import liquitrader

# from io import BytesIO

import flask
from flask import jsonify, Response

import flask_compress
import flask_login

from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_otp import OTP
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm

import pandas as pd

# import pyqrcode

import requests

# from wtforms import StringField, PasswordField, SubmitField, BooleanField
# from wtforms.validators import DataRequired, Length


LT_ENGINE = None
FRIENDLY_MARKET_COLUMNS = liquitrader.FRIENDLY_MARKET_COLUMNS


class LiquitraderFlaskApp:
    app = flask.Flask('liquitrader_flask_app')

    database_uri = f'sqlite:///{liquitrader.APP_DIR / "config" / "liquitrader.db"}'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    database = SQLAlchemy(app)

    login_man = flask_login.LoginManager(app)

    otp = OTP()
    otp.init_app(app)

    CORS(app)
    bootstrap = Bootstrap(app)
    flask_compress.Compress(app)

    # ----
    def __init__(self, shutdown_handler, ssl=False):
        self.shutdown_handler = shutdown_handler
        self._use_ssl = ssl

    def run(self):
        self.shutdown_handler.add_task()
        self.app.run('0.0.0.0', 80)

    def stop(self):
        # TODO: SHUTDOWN CHEROOT HERE
        _ = requests.get('http://localhost/shutdown')
        self.shutdown_handler.remove_task()

    @app.route("/shutdown", methods=['GET'])
    def shutdown(self):
        # TODO: This only works for Flask
        app_stop_func = flask.request.environ.get('werkzeug.server.shutdown')

        if app_stop_func is not None:
            app_stop_func()
            return flask.Response(status=200)

        else:
            print('Failed to shutdown GUI')
            return flask.Response(status=500)

    @app.route("/")
    def gethello(self):
        return "hello"

    @app.route("/holding")
    def get_holding(self):
        df = LT_ENGINE.pairs_to_df(friendly=True)

        if 'Amount' not in df:
            return jsonify([])

        df[df['Amount'] > 0].to_json(orient='records', path_or_buf='holding')
        return jsonify(df[df['Amount'] > 0].to_json(orient='records'))

    @app.route("/market")
    def get_market(self):
        df = LT_ENGINE.pairs_to_df(friendly=True)
        df[FRIENDLY_MARKET_COLUMNS].to_json(orient='records', path_or_buf='market')

        return jsonify(df[FRIENDLY_MARKET_COLUMNS].to_json(orient='records'))

    @app.route("/buy_log")
    def get_buy_log_frame(self):
        df = pd.DataFrame(LT_ENGINE.trade_history)
        df['gain'] = (df.price - df.bought_price) / df.bought_price * 100
        df['net_gain'] = (df.price - df.bought_price) * df.filled

        if 'price' not in df:
            return jsonify([])

        cols = ['datetime', 'symbol', 'price', 'amount', 'side', 'status', 'remaining', 'filled']

        df[df.side == 'buy'][cols].to_json(orient='records', path_or_buf='buy_log')

        return jsonify(df[df.side == 'buy'][cols].to_json(orient='records'))

    @app.route("/sell_log")
    def get_sell_log_frame(self):
        df = pd.DataFrame(LT_ENGINE.trade_history)

        if 'price' not in df:
            return jsonify([])

        df['gain'] = (df.price - df.bought_price) / df.bought_price * 100
        cols = ['datetime', 'symbol', 'bought_price', 'price', 'amount', 'side', 'status', 'remaining', 'filled',
                'gain']
        df[df.side == 'sell'][cols].to_json(orient='records', path_or_buf='sell_log')

        return jsonify(df[df.side == 'sell'][cols].to_json(orient='records'))

    @app.route("/dashboard_data")
    def get_dashboard_data(self):
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
    def update_config(self):
        data = flask.request.data.decode()
        LT_ENGINE.config.update_config(data['section'], data['data'])

        return data

    @app.route("/config")
    def get_config(self):
        return jsonify(str(vars(LT_ENGINE.config)))


