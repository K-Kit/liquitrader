import random
import base64


server_pub_der_b64 = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzbnblK3WAQlf/vLDBv89OkSo2RbcBxFrd8nFfEjUZNvDAS2YMDyeKNNvLqZwvC1iOGcZ/dw1fIwFfL/6JMzeoLmsTNwsHzj4PZXIv6YkKOT47eXdUBEhHmXavqWg1tI9tUiUv5zEi9g+LbZJ8xp45mUy7Xblb46C25FiOuUM5z70eC+cANSpxVq6jYQ6Bvy+I6T54gydT8INHX9IahIi3nkHa2323+x7Q6s85W+62lXylGx/qKxkwg9+0NjOqbtteh8r9C2W1xh9dTmweIONLrFI7rUhZKp8q+O5/E7pP1zucmezhxp6JW7Pl5QC4At96CD4+Kp4jAEoqXuRtjywFwIDAQAB'

liqui_priv_der_b64 = 'MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCb6a12fEWcHcjkkd1tlG85d5EBeCwrteCvykpOEkffncGZDXvCD00JaxLqiKk6pcEv9OKDQhVdPhNKnogWG2d5xY0K6+a0/KK4Rf2QoUprnyptdyUmmuPug3m+QQ+8EF6R8dlQ9KnKm9tuCSjMGHfWrxhmxaXeWoFyY0R1EQiPCMSbELXG4T02YnzYY0a7zl8P9Ek6ouHoZ6mplc2Z/5b6Q+bbr2iuZ8czZwcP8wXWQwTAI/STdlW7992hACRlcCKU1Fq1R/uftBCSO8oNwIbw0yoNEWzduMyA6O2F+NVvGnQySrRLuK7yRD2dLmCmPluwH1qBW0lpfGhypUCuR6fxAgMBAAECggEAKyyWYE0haY3F56WMz59e/WbivKlucdw3j/ZQhTYCuSWSSrO1JZPfHVCNOG0Hj7n+uSzy3K4cBGoAJZWo0ZZdHRdbaz7P8CZVWPnosXg4h3zX3uAzZXFW1OGLgOe7V7Sgu4FhUE2wBu8J4Hqg1YOhC84Iz8zDlcMyPV7HwjMpT5ILWLUJEdvoxy82QRWXF7aOxwJPUtREZiHI2o3DdyxMmwtTr2Y+3kviu6qXKxeAqRNSpkUbzZ3C6J2kn3Wbw1t+2HV/H67qMtEZvmSddqlMaEHybssXax3JXqUL8850mfEL2tgQRVsN7mcb85NsqmY3974GfUFWp5eKrKVOFxU3wQKBgQDJkIXlMRxJBu+nnczxP1lFRHDYC3rh8kDTA73cn8kofa8HR1IBePwz+KR4v9R9dLWqDQb3BQsssvMUuTm2i9Ce1DDG/wGhHsSdLhbkUAXiFVpwr76M2icAIwD+Q4dTmtLN8WtOmyt4FPYI2KDaPYk2sAse6M6UzuNSrQW5+NO7dQKBgQDGBPNmzckXk5pd1Fjw6yPQTr4XVvENhq5/lFCbFd06E76zwV1fBPgAlmAcXgTAAgZjwvjZZ+oqWxv1PWWO9TmxZqLn4aMIfmf3bsZxr2ojgmZZF9fWY/uWlndUh8F0nsQKhafjNxQGCU1iCgVP0gMll+P1Pn9yZ4Ce/qtHyh03DQKBgERJhUNHpxiKlAjKalNVLe5MqJpZEVGZHCMhQmKLc8AXDIQ/wmWjUnZdB4OtIdU7BAzPiwuHFukW20mrEwVoSs50fu38GNY4MU46/iBtiAC3UUOaFslrYwkl0sFRqXhGnKKO5tbjtQ9ispP+qEgnzuPLMolPQCWkDdnFqon95eW9AoGABQTJGnjquNM/3VLtciWzgasNPFAyydH5CDi9FkEmmzs24R1sfWUF2BX3l6B2ZFtoyAx//BqbH7mxarTEpyvl624bgN8CH8v8XJQNKYJ1oTLD30wwZzmffcCQg67xI0CG3XFnwOV7d2+y62IvokdDVyeTWnrcBg1DgEQaGTaxKN0CgYA/DQ+dcXT9wqk1hC7DdZPFlOSzljkVEmLNYnYl5e7Mz+QnCoIEA0uTF7CxfjaOMo9NSPeNbPyn/nC17HiHHgGh5oYTFasMYT5ZhOYFaPc0dvCBUu52Yb5w0VVO2DFstCHG/6PXxGreN5dfakFyAyZTzHA0PHjZtxMTpMyOLuyg7g=='


def scramble(key: str):
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
                encoded += f'{len(cur_run) + 1}{ch}'

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

    rl_encoded = rle(key)
    rl_encoded_shifted = shift(rl_encoded)
    rl_encoded_shifted_b64 = base64.b64encode(rl_encoded_shifted.encode()).decode('utf-8')

    eq_count = rl_encoded_shifted_b64[-9:].count('=')

    rl_encoded_shifted_b64_obfusc = f'{rl_encoded_shifted_b64[:315]}{eq_count}{rl_encoded_shifted_b64[315:]}'.rstrip('=')

    return rl_encoded_shifted_b64_obfusc


def unscramble(scrambled: str):
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

    re_padded = f'{scrambled[:315]}{scrambled[316:]}{("=" * int(scrambled[315]))}'.encode()
    rl_decoded_shifted = base64.b64decode(re_padded).decode('utf-8')
    rl_decoded_unshifted = unshift(rl_decoded_shifted)
    rl_decoded = rld(rl_decoded_unshifted)

    return rl_decoded


if __name__ == '__main__':
    pub_scrambled = scramble(server_pub_der_b64)
    priv_scrambled = scramble(liqui_priv_der_b64)

    print('Scrambled:')
    print(pub_scrambled)
    print()
    print(priv_scrambled)

    print('\n\n\n')
    print('Unscrambled:')
    pub_unscrambled = unscramble(pub_scrambled)
    priv_unscrambled = unscramble(priv_scrambled)

    print(pub_unscrambled)
    print()
    print(priv_unscrambled)
    print()
    print(f'Pub match: {server_pub_der_b64 == pub_unscrambled}')
    print(f'Priv match: {liqui_priv_der_b64 == priv_unscrambled}')
