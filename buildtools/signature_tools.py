import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils


class SignTool:

    def __init__(self, private_key_filename='liquitrader.pem'):
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
        hash_alg = hashes.SHA256()
        hasher = hashes.Hash(hash_alg, default_backend())

        # Load the contents of the file to be signed.
        with open(filename, 'rb') as f:
            chunk = f.read(1024)
            while chunk != '':
                hasher.update(chunk)
                chunk = f.read(1024)

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
        return {filename: self.get_file_signature(filename) for filename in files}
