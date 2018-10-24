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

        def __init__(self, private_key_string):
            private_key = serialization.load_pem_private_key(bytes(private_key_string, encoding='utf-8'),
                                                             default_backend())
            self.public_key = private_key.public_key()

        # ----
        def verify_file(self, filename, signature_b64):
            signature = base64.b64decode(signature_b64)

            hash_alg = hashes.SHA256()
            hasher = hashes.Hash(hash_alg, default_backend())

            # Load the contents of the file to be signed.
            with open(filename, 'rb') as file_to_check:
                chunk = file_to_check.read(1024)
                while chunk != '':
                    hasher.update(chunk)
                    chunk = file_to_check.read(1024)

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

            except cryptography.exceptions.InvalidSignature as e:
                return False

        # ----
        def verify_files(self, file_signature_dict):
            return all(iter(self.verify_file(file, signature_b64) for file, signature_b64 in file_signature_dict))


    verifier = VerifyTool({public_key_string})

    if not verifier.verify_files({signature_dict}):
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
    with open('liquitrader.pem') as signature_file:
        private_key = signature_file.read()

    signer = buildtools.signature_tools.SignTool()
    file_signature_dict = signer.sign_files(to_sign)

    with open('runner.py', 'w') as runner_file:
        print(runner_template.format(private_key_string=private_key,
                                     signature_dict=file_signature_dict),
              file=runner_file)
