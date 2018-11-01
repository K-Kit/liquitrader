import os
import sys
from distutils.sysconfig import get_python_lib


def patch_strptime_patcher():
    if sys.platform == 'win32':
        strptime_monkeypatch_path = get_python_lib()
    else:
        strptime_monkeypatch_path = '/usr/local/lib/python3.6/dist-packages'
        
    strptime_monkeypatch_path = os.path.join(strptime_monkeypatch_path, 'dateparser', 'utils', 'strptime.py')

    with open(strptime_monkeypatch_path, 'r') as f:
        data = f.read()
        
    # Patch already done
    if 'from zipimport' in data:
        return

    data = data.replace('import imp', '''\
# ~~~~~~~~~~~~
# LIQUITRADER MONKEY-PATCH

from zipimport import zipimporter, ZipImportError

try:
    zimp = zipimporter('lib/library.zip/')

    import importlib

    class imp:
        @staticmethod
        def find_module(name, *args, **kwargs):
            return [name]

        @staticmethod
        def load_module(_, fullname, *args, **kwargs):
            try:
                return zimp.load_module(fullname)

            except ZipImportError:
                return importlib.import_module(fullname)

except ZipImportError:
    import imp
# ~~~~~~~~~~~~
''')

    with open(strptime_monkeypatch_path, 'w') as f:
        f.write(data)


def do_patches():
    patch_strptime_patcher()


if __name__ == '__main__':
    do_patches()
