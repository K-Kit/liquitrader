from cryptography.hazmat.primitives import serialization

import buildtools.signature_tools


runner_template = """\
if __name__ == '__main__':
    import base64
    import sys

    import cryptography.exceptions
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, utils


    class VerifyTool:

        def __init__(self, public_key_bytes):
            self.public_key = serialization.load_pem_public_key(public_key_bytes, default_backend())

        # ----
        def verify_file(self, filename, signature_b64):
            signature = base64.b64decode(signature_b64)

            hash_alg = hashes.SHA256()
            hasher = hashes.Hash(hash_alg, default_backend())

            # Load the contents of the file to be signed.
            with open('./lib/' + filename, 'rb') as file_to_check:
                chunk = file_to_check.read(2048)
                while chunk != b'':
                    hasher.update(chunk)
                    chunk = file_to_check.read(2048)

            digest = hasher.finalize()

            # Perform the verification
            try:
                self.public_key.verify(
                    signature,
                    digest,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH,
                    ),
                    utils.Prehashed(hash_alg)
                )

                return True

            except cryptography.exceptions.InvalidSignature:
                return False

        # ----
        def verify_files(self, file_signature_dict):
            return all(iter(self.verify_file(file, signature_b64) for file, signature_b64 in file_signature_dict))


    verifier = VerifyTool({public_key_string})

    if not verifier.verify_files({signature_tuples}):
        sys.stdout.writeline('LiquiTrader file signature verification failed!')
        sys.stdout.writeline('LiquiTrader has been illegitimately modified and must be reinstalled.')
        sys.stdout.writeline('We recommend downloading it manually from our website in case your updater has been compromised.')
        sys.stdout.flush()

        sys.exit(1)


    # ~~~
    import liquitrader
    liquitrader.main()
"""


def build_runner(to_sign):
    signer = buildtools.signature_tools.SignTool()
    file_signature_tuples = signer.sign_files(to_sign)

    public_key_bytes = signer.public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open('runner.py', 'w') as runner_file:
        print(runner_template.format(public_key_string=public_key_bytes,
                                     signature_tuples=file_signature_tuples),
              file=runner_file)
