import sys
from distutils.sysconfig import get_python_lib
import site

import tempfile
import zipfile
import shutil
import os


def remove_from_zip(zipfname, *filenames):
    tempdir = tempfile.mkdtemp()

    try:
        tempname = os.path.join(tempdir, 'new.zip')

        with zipfile.ZipFile(zipfname, 'r') as zipread:
            with zipfile.ZipFile(tempname, 'w') as zipwrite:
                for item in zipread.infolist():
                    if item.filename not in filenames:
                        data = zipread.read(item.filename)
                        zipwrite.writestr(item, data)

        shutil.move(tempname, zipfname)

    finally:
        shutil.rmtree(tempdir)


def strptime_patcher():
    #if sys.platform == 'win32':
    found = False

    for lib_path in (site.getusersitepackages(), get_python_lib(True)):
        strptime_monkeypatch_path = os.path.join(lib_path, 'dateparser', 'utils', 'strptime.py')

        if os.path.exists(strptime_monkeypatch_path):
            found = True
            break

    if not found:
        print('ERROR: Could not find dateparser/utils/strptime.py in site packages')
        sys.exit(1)

    # else:
    #     paths = [
    #         '/usr/local/lib/python3.6/dist-packages/dateparser/utils/strptime.py',
    #
    #     strptime_monkeypatch_path =
    #
    #     if not os.path.isfile(strptime_monkeypatch_path):
    #         strptime_monkeypatch_path = '/usr/local/lib/python3.6/site-packages'
    #         strptime_monkeypatch_path = os.path.join(strptime_monkeypatch_path, 'dateparser', 'utils', 'strptime.py')

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


def do_prebuild_patches():
    strptime_patcher()


def do_postbuild_patches():
    pass
