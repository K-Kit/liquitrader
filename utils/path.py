import sys
import os
import pathlib


APP_DIR = ''


def set_path():
    global APP_DIR

    if hasattr(sys, 'frozen'):
        APP_DIR = pathlib.Path(os.path.dirname(sys.executable)).absolute()
        os.chdir(APP_DIR)
        os.environ["REQUESTS_CA_BUNDLE"] = str(APP_DIR / 'lib' / 'cacert.pem')

    else:
        APP_DIR = pathlib.Path(os.path.dirname(__file__)).absolute().parent
