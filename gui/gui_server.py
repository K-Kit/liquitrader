import binascii
import os
# from io import BytesIO
import pathlib
import sys
import psutil

from liquitrader import FRIENDLY_MARKET_COLUMNS, APP_DIR

from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher
from cheroot.ssl.builtin import BuiltinSSLAdapter

import flask
from flask import jsonify, Response, render_template

import flask_compress
import flask_login

from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_otp import OTP
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm

from OpenSSL import crypto

import pandas as pd
# import pyqrcode

from utils.FormattingTools import eight_decimal_format, decimal_with_usd

# from wtforms import StringField, PasswordField, SubmitField, BooleanField
# from wtforms.validators import DataRequired, Length


LT_ENGINE = None
# FRIENDLY_MARKET_COLUMNS = liquitrader.FRIENDLY_MARKET_COLUMNS
_cmdline = psutil.Process().cmdline()
abs_path = pathlib.Path(_cmdline[len(_cmdline) - 1]).absolute().parent
bearpuncher_dir = abs_path

if hasattr(sys, 'frozen'):
    dist_path = abs_path / 'static'
else:
    dist_path = abs_path / 'LTGUI' / 'build'
_app = flask.Flask('lt_flask', static_folder=dist_path / 'static', template_folder=dist_path)



def to_usd(val):
    return f'${round(val*LT_ENGINE.exchange.quote_price, 2)}'


class GUIServer:

    def __init__(self, shutdown_handler, host='localhost', port=5000, ssl=False):
        database_uri = f'sqlite:///{APP_DIR / "config" / "liquitrader.db"}'
        _app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        _app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self._database = SQLAlchemy(_app)

        self._login_man = flask_login.LoginManager(_app)

        otp = OTP()
        otp.init_app(_app)
        CORS(_app)
        self._bootstrap = Bootstrap(_app)
        flask_compress.Compress(_app)

        self._shutdown_handler = shutdown_handler
        self._host = host
        self._port = port

        self._use_ssl = ssl
        self._certfile_path = APP_DIR / 'lib' / 'liquitrader.crt'
        self._keyfile_path = APP_DIR / 'lib' / 'liquitrader.key'

        # Set constants for WSGIServer
        WSGIServer.version = 'LiquiTrader/2.0'

        self._wsgi_server = None

    # ----
    def _create_self_signed_cert(self):
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 2048)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = 'US'
        cert.get_subject().O = 'LiquiTrader'
        cert.get_subject().CN = 'localhost'
        cert.set_serial_number(int(binascii.hexlify(os.urandom(16)), 16))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, b'sha256')

        with open(self._certfile_path, 'wb') as certfile:
            certfile.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        with open(self._keyfile_path, 'wb') as keyfile:
            keyfile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

    # --
    def _init_ssl(self):
        import flask_sslify
        flask_sslify.SSLify(_app, permanent=True)

        if not (os.path.exists(self._certfile_path) and os.path.exists(self._keyfile_path)):
            self._create_self_signed_cert()

        WSGIServer.ssl_adapter = BuiltinSSLAdapter(certificate=self._certfile_path, private_key=self._keyfile_path)

    # ----
    def run(self):
        self._shutdown_handler.add_task()

        if self._use_ssl:
            self._init_ssl()

        self._wsgi_server = WSGIServer((self._host, self._port), PathInfoDispatcher({'/': _app}))

        # TODO: Issue with SSL:
        # Firefox causes a (socket.error 1) exception to be thrown on initial connection (before accepting cert)
        # This is internal to cheroot, so it may be difficult to handle

        print('LiquiTrader is ready for action!')
        print(f'Visit http{"s" if self._use_ssl else ""}://{self._host}:{self._port} in your favorite browser')
        print('to start trading!')

        self._wsgi_server.start()

    # ----
    def stop(self):
        self._wsgi_server.stop()
        self._shutdown_handler.remove_task()


# ----
@_app.route('/')
@_app.route('/<path:path>')
def get_index(path=None):
    return render_template('index.html')


# ----
@_app.route("/api/holding")
def get_holding():
    df = LT_ENGINE.pairs_to_df(friendly=True)

    if 'Amount' not in df:
        return jsonify([])

    return jsonify(df[df['Amount'] > 0].to_json(orient='records'))


# ----
@_app.route("/api/market")
def get_market():
    df = LT_ENGINE.pairs_to_df(friendly=True)

    return jsonify(df[FRIENDLY_MARKET_COLUMNS].to_json(orient='records'))


# ----
@_app.route("/api/buy_log")
def get_buy_log_frame():
    df = pd.DataFrame(LT_ENGINE.trade_history)

    if len(df) < 1:
        return jsonify([])

    cols = ['timestamp', 'symbol', 'price', 'amount', 'side', 'status', 'remaining', 'filled']

    return jsonify(df[df.side == 'buy'][cols].to_json(orient='records'))


# ----
@_app.route("/api/sell_log")
def get_sell_log_frame():
    df = pd.DataFrame(LT_ENGINE.trade_history)

    if 'bought_price' not in df:
        return jsonify([])
    df['bought_cost'] = df.bought_price * df.filled
    df['gain'] = (df.cost - df.bought_cost) / df.bought_cost * 100
    cols = ['timestamp', 'symbol', 'bought_price', 'price','cost', 'bought_cost', 'amount', 'side', 'status', 'remaining', 'filled', 'gain']


    return jsonify(df[df.side == 'sell'][cols].dropna().to_json(orient='records'))


# ----
def latest_sales():
    df = pd.DataFrame(LT_ENGINE.trade_history)

    if 'bought_price' not in df:
        return []
    df['bought_cost'] = df.bought_price * df.filled
    df['gain'] = (df.cost - df.bought_cost) / df.bought_cost * 100
    cols = ['symbol', 'gain']
    df=df[df.side == 'sell'][cols].dropna().tail(4)


    return df.to_dict(orient="records")


# ----
@_app.route("/api/dashboard_data")
def get_dashboard_data():
    balance = LT_ENGINE.exchange.balance
    pending = LT_ENGINE.get_pending_value()
    current = LT_ENGINE.get_tcv()
    profit = LT_ENGINE.get_total_profit()
    profit_data = LT_ENGINE.get_daily_profit_data()
    total_profit = LT_ENGINE.get_total_profit()
    average_daily_gain = profit / len(profit_data)
    market = LT_ENGINE.config.general_settings['market'].upper()
    recent_sales = latest_sales()
    def reorient(df):
        # return [{k: v for (k, v) in row.items() if k != 'foo'} for row in df.to_dict(orient='record')]
        return [{col: getattr(row, col) for col in df} for row in df.itertuples()]

    data = {
        "quote_balance": eight_decimal_format(balance),
        "total_pending_value": eight_decimal_format(pending),
        "total_current_value": eight_decimal_format(current),
        "total_profit": eight_decimal_format(profit),
        "market": f"{market}",
        "usd_balance_info": f"{to_usd(balance)} / {to_usd(pending)}",
        "usd_total_profit": f"{to_usd(profit)}",
        "usd_average_daily_gain": f"{to_usd(average_daily_gain)}",
        "market_change_24h": f"{round(LT_ENGINE.market_change_24h, 2)}%",
        "average_daily_gain": f"{round(average_daily_gain / pending*100, 2)}",
        "total_profit_percent": f"{round(total_profit / balance * 100, 2)}%",
        "daily_profit_data": reorient(profit_data[profit_data.percent_gain < 9999]),
        "holding_chart_data": LT_ENGINE.pairs_to_df()['total_cost'].dropna().to_json(orient='records'),
        "cum_profit": reorient(LT_ENGINE.get_cumulative_profit()),
        "recent_sales": recent_sales,
        "pair_profit_data": reorient(LT_ENGINE.get_pair_profit_data()),
        "quote_candles": reorient(LT_ENGINE.exchange.quote_candles.tail(24)),
        "market_conditions": [[f"Below Max Pairs: ", str(LT_ENGINE.below_max_pairs)],
                              [f"1h {market} change in range: ", str(LT_ENGINE.check_1h_quote_change)],
                              [f"24h {market} change in range: ", str(LT_ENGINE.check_24h_quote_change)],
                              [f"24h Market Average Change in range:", str(LT_ENGINE.check_24h_market_change)]
                              ]
    }

    return jsonify(data)


# ----
@_app.route('/api/update_config', methods=['POST'])
def update_config():
    data = flask.request.get_json(force=True)
    print(data)
    LT_ENGINE.config.update_config(data['section'], data['data'])

    return 'hello'


# ----
@_app.route("/api/config")
def get_config():
    return LT_ENGINE.config.get_config()


# ----
@_app.route("/api/analyzers")
def get_analyzers():
    import json
    import numpy
    return jsonify(LT_ENGINE.get_trailing_pairs())



