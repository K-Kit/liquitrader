import os
import sys
import time
import shutil
import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils, rsa


def generate_private_key(filename='./buildtools/liquitrader.pem'):
    if os.path.exists(filename):
        if input('This will overwrite (and backup) the existing private key!\n'
                 'Are you sure you want to do this? ') != 'y':
            return

        if input('Really? ') != 'y':
            return

        shutil.copy(filename, f'{filename}.bak.{time.time()}')

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(filename, 'wb') as pem_out:
        pem_out.write(pem)


class SignTool:

    def __init__(self, private_key_filename='./buildtools/liquitrader.pem'):
        self.private_key_filename = private_key_filename
        self.private_key = None
        self.public_key = None

        self._populate_keys()

    # ----
    def _populate_keys(self):
        # Load the private key.
        with open(self.private_key_filename, 'rb') as key_file:
            self.private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend(),
            )

        self.public_key = self.private_key.public_key()

    # ----
    def get_file_signature(self, filename):
        if not os.path.exists(filename):
            print(f'{filename} does not exist')
            return None

        hash_alg = hashes.SHA256()
        hasher = hashes.Hash(hash_alg, default_backend())

        # Load the contents of the file to be signed.
        with open(filename, 'rb') as f:
            chunk = f.read(2048)
            while chunk != b'':
                hasher.update(chunk)
                chunk = f.read(2048)

        digest = hasher.finalize()

        # Sign the payload file.
        return base64.b64encode(
            self.private_key.sign(
                digest,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                utils.Prehashed(hash_alg)
            )
        )

    # ----
    def sign_files(self, files):
        output = []

        for filename in files:
            print(f'Generating signature for {filename}')
            signature = self.get_file_signature(filename)

            if signature is not None:
                clean_fname = filename.replace(os.path.sep, '/').replace('./', '')
                new_path = '/'.join(clean_fname.split('/')[2:])

                encoded = base64.b64encode(new_path.encode())
                output.append((encoded, signature))

        return output
