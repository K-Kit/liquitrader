import random
import base64

from cryptography.hazmat.primitives import serialization

import buildtools.signature_tools


runner_template = r"""
import base64
import sys
import os

import cryptography.exceptions
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils


class VerifyTool:

    def __init__(self, verifier_data):
        rl_decoded_shifted = base64.b64decode(verifier_data).decode('utf-8')
        rl_decoded_unshifted = unshift(rl_decoded_shifted)
        rl_decoded = rld(rl_decoded_unshifted).encode()
        rl_decoded = base64.b64decode(rl_decoded)

        self.public_key = serialization.load_der_public_key(rl_decoded, default_backend())

    # ----
    def verify_file(self, filename, signature_b64):
        if not os.path.exists(filename):
            print(f'Error: {{filename}} does not exist.')
            return False

        signature = base64.b64decode(signature_b64)

        hash_alg = hashes.SHA256()
        hasher = hashes.Hash(hash_alg, default_backend())

        # Load the contents of the file to be signed.
        with open(filename, 'rb') as file_to_check:
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
    def verify_files(self, tuples):
        for file, signature_b64 in tuples:
            if not self.verify_file(base64.b64decode(file).decode('utf-8'), signature_b64):
                sys.stdout.write(file, 'failed to verify')
                sys.stdout.flush()
                return False
        
        return True
            
        # return all(iter(self.verify_file(base64.b64decode(file).decode('utf-8'), signature_b64) for file, signature_b64 in tuples))


def rld(string):
    decoded = ''

    for run_length_pos in range(0, len(string), 2):
        decoded += string[run_length_pos + 1] * int(string[run_length_pos])

    return decoded


def unshift(string):
    split = string.find('~')
    key, shifted = string[:split], string[split + 1:]
    shift_table = []
    
    next_neg = False
    for sh in key:
        if sh == '-':
            next_neg = True
            continue
        
        shift_table.append(int(sh) * -1 if next_neg else int(sh))
        next_neg = False

    unshifted = ''
    for ch, shift_amt in zip(shifted, shift_table):
        unshifted += chr(ord(ch) - shift_amt)

    return unshifted


def err_msg():
    sys.stdout.write('LiquiTrader has been illegitimately modified and must be reinstalled.\n')
    sys.stdout.write('We recommend downloading it manually from our website in case your updater has been compromised.\n\n')
    sys.stdout.flush()


def verify():
    verifier = VerifyTool('{verifier_data}')

    if not verifier.verify_files({signature_tuples}):
        err_msg()
        sys.exit(1)

if __name__ == '__main__':
    import sys
    print('This library is not allowed to run standalone')
    sys.exit(1)
"""


def rle(string):
    encoded = ''
    cur_run = ''
    prev_ch = string[0]

    last_string_pos = len(string) - 2

    for pos, ch in enumerate(string[1:]):
        if ch == prev_ch:
            cur_run += ch
        else:
            encoded += f'{len(cur_run) + 1}{prev_ch}'
            cur_run = ''

        if pos == last_string_pos:
            encoded += f'{len(cur_run) + 1}{prev_ch}'

        prev_ch = ch

    return encoded


def shift(string):
    key = ''
    shifted = ''

    for ch in string:
        shift_num = random.randint(-9, 9)
        key += str(shift_num)
        shifted += chr(ord(ch) + shift_num)

    return key + '~' + shifted


def build_verifier(to_sign):
    signer = buildtools.signature_tools.SignTool()
    file_signature_tuples = signer.sign_files(to_sign)

    public_key_b64 = base64.b64encode(signer.public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )).decode('utf-8')

    server_pub_rl_encoded = rle(public_key_b64)
    server_pub_rl_encoded_shifted = shift(server_pub_rl_encoded)
    server_pub_rl_encoded_shifted_b64 = base64.b64encode(server_pub_rl_encoded_shifted.encode()).decode('utf-8')

    with open('strategic_analysis.py', 'w') as runner_file:
        print(runner_template.format(verifier_data=server_pub_rl_encoded_shifted_b64,
                                     signature_tuples=file_signature_tuples),
              file=runner_file)
