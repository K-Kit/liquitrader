import os
import base64

import onetimepass
import scrypt

from cryptography.hazmat.primitives.constant_time import bytes_eq
from cryptography.hazmat.primitives.ciphers.aead import AESCCM

from flask_login import UserMixin


def create_user_database_model(database):
    class User(UserMixin, database.Model):
        __tablename__ = 'users'

        id = database.Column(database.Integer, primary_key=True)
        username = database.Column(database.String(64), index=True, unique=True)

        salt = database.Column(database.String(56))
        password_hash = database.Column(database.String(128))

        tfa_secret = database.Column(database.String(16))
        tfa_active = database.Column(database.Integer)

        role = database.Column(database.String(15))

        def __init__(self, **kwargs):
            super(User, self).__init__(**kwargs)

            # Password salt
            if self.salt is None:
                self.salt = base64.b32encode(os.urandom(32)).decode('utf-8')

            if self.role is None:
                self.role = 'admin'

            if self.tfa_secret is None:
                self.tfa_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

            if self.tfa_active is None:
                self.tfa_active = 0

        @property
        def password(self):
            raise AttributeError('password is not a readable attribute')

        @password.setter
        def password(self, password):
            if self.salt is None:
                self.salt = base64.b32encode(os.urandom(32)).decode('utf-8')

            self.password_hash = base64.b64encode(scrypt.hash(base64.b64decode(self.salt), password, buflen=128)).decode('utf-8')

        def verify_password(self, password):
            return bytes_eq(scrypt.hash(base64.b64decode(self.salt), password, buflen=128),
                            base64.b64decode(self.password_hash.encode()))

        def get_totp_uri(self):
            return 'otpauth://totp/Liquitrader:{0}?secret={1}&issuer=Liquitrader'.format(self.username, self.tfa_secret)

        def verify_totp(self, token):
            return onetimepass.valid_totp(token, self.tfa_secret)

    return User


def create_keystore_database_model(database):
    class KeyStore(database.Model):
        __tablename__ = 'keystore'

        id = database.Column(database.Integer, primary_key=True)

        bearpuncher_license = database.Column(database.String(50))
        exchange_key_public = database.Column(database.String(50))
        exchange_key_private = database.Column(database.String(50))

        master_key = database.Column(database.String(60))
        master_nonce = database.Column(database.String(30))

        def __init__(self, **kwargs):
            super(KeyStore, self).__init__(**kwargs)

            if self.master_key is None:
                self.master_key = self._to_b32(AESCCM.generate_key(256))

            if self.master_nonce is None:
                self.master_nonce = self._to_b32(os.urandom(13))

        # ----
        def _to_b32(self, data):
            return base64.b32encode(data).decode('utf-8')

        # --
        def _from_b32(self, data):
            return base64.b32decode(data.encode())

        # ----
        def _get_engine(self):
            return AESCCM(self._from_b32(self.master_key))

        # ----
        def _encrypt(self, data):
            engine = self._get_engine()
            master_nonce = self._from_b32(self.master_nonce)

            return self._to_b32(engine.encrypt(master_nonce, bytes(data, 'utf-8'), b''))

        # --
        def _decrypt(self, data):
            engine = self._get_engine()
            master_nonce = self._from_b32(self.master_nonce)
            data = self._from_b32(data)

            return engine.decrypt(master_nonce, data, b'')

        # ----
        @property
        def public_exchange_key(self):
            # Decrypt public key and return
            return str(self._decrypt(self.exchange_key_public))[2:-1]

        # --
        @public_exchange_key.setter
        def public_exchange_key(self, value):
            # Encrypt public key and store
            self.exchange_key_public = self._encrypt(value)

        # ----
        @property
        def private_exchange_key(self):
            # Decrypt private key and return
            return str(self._decrypt(self.exchange_key_private))[2:-1]

        # --
        @private_exchange_key.setter
        def private_exchange_key(self, value):
            # Encrypt private key and store
            self.exchange_key_private = self._encrypt(value)

        # ----
        @property
        def bearpuncher_license_key(self):
            # Decrypt private key and return
            return str(self._decrypt(self.bearpuncher_license))[2:-1]

        # --
        @bearpuncher_license_key.setter
        def bearpuncher_license_key(self, value):
            # Encrypt bearpuncher license and store
            self.bearpuncher_license = self._encrypt(value)

    return KeyStore


def create_flask_database_model(database):
    class FlaskStore(database.Model):
        __tablename__ = 'flaskstore'

        id = database.Column(database.Integer, primary_key=True)
        session_secret = database.Column(database.String(20))
        wtf_crsf_secret = database.Column(database.String(20))

        def __init__(self):
            if self.session_secret is None or self.wtf_crsf_secret is None:
                self.session_secret = os.urandom(16)
                self.wtf_crsf_secret = os.urandom(16)

    return FlaskStore


def migrate_table(database):
    user_column_defs = ', '.join([
        'id INTEGER NOT NULL',
        'username VARCHAR(64) NOT NULL',
        'salt VARCHAR(56) NOT NULL',
        'password_hash VARCHAR(128) NOT NULL',
        'tfa_active INTEGER',
        'tfa_secret VARCHAR(16)',
        'role VARCHAR(15)',
        'PRIMARY KEY (id)'
    ])

    # role = database.Column(database.String(15), index=True)
    # version = database.Column(database.Integer)

    # TODO: ADD ROLE TO USERS TABLE

    with database.engine.begin() as conn:
        existing_cols = [_[1] for _ in conn.execute('PRAGMA table_info(users)').fetchall()]

        if 'role' in existing_cols:  # This is a current (8/20/18) indication of an up-to-date database
            return

        conn.execute('ALTER TABLE users RENAME TO _users_old')

        conn.execute('CREATE TABLE users ( {} )'.format(user_column_defs))

        if 'tfa_active' in existing_cols:
            conn.execute('INSERT INTO users ( id, username, password_hash, tfa_active, tfa_secret, role ) '
                             'SELECT id, username, password_hash, tfa_active, tfa_secret, "admin" '
                             'FROM _users_old'
                         )

        else:
            conn.execute('INSERT INTO users ( id, username, password_hash, tfa_active, role ) '
                            'SELECT id, username, password_hash, 0, "admin" '
                            'FROM _users_old'
                         )

        conn.execute('DROP TABLE _users_old')