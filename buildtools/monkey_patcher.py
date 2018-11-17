import sys
import site
import zipfile
import os
import shutil
import py_compile
import tempfile

from distutils.sysconfig import get_python_lib


def replace_in_zip(zipfname, file_pairs):
    """file_pairs = [ [path_in_archive, path_to_replacement], ]"""

    tempdir = tempfile.mkdtemp()

    try:
        tempname = os.path.join(tempdir, 'new.zip')

        with zipfile.ZipFile(zipfname, 'r') as zipread:
            with zipfile.ZipFile(tempname, 'w', compression=zipfile.ZIP_DEFLATED) as zipwrite:
                for item in zipread.infolist():
                    if item.filename == 'twisted/internet/error.pyc':
                        try:
                            zipwrite.write(file_pairs[0][1], arcname=file_pairs[0][0])

                        except PermissionError:
                            print(f'Failed to zip {file_pairs[0][1]}')

                    else:
                        data = zipread.read(item.filename)
                        zipwrite.writestr(item, data)

        os.remove(zipfname)
        shutil.move(tempname, zipfname)

    finally:
        shutil.rmtree(tempdir)


def get_library_filepath(partial_path):
    """Partial path such as 'dateparser/utils/strptime.py'"""

    for lib_path in (site.getusersitepackages(), get_python_lib(True)):
        path = os.path.join(lib_path, partial_path)

        if os.path.exists(path):
            return path

    return None


def strptime_patcher():
    strptime_path = get_library_filepath('dateparser/utils/strptime.py')

    if strptime_path is None:
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

    with open(strptime_path, 'r') as f:
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

    with open(strptime_path, 'w') as f:
        f.write(data)


# --------
def twisted_error_patcher(build_path=None):
    if build_path is None:
        build_path = './build/liquitrader_win/' if sys.platform == 'win32' else './build/liquitrader_linux/'
        build_path = os.path.abspath(build_path)

    error_path = get_library_filepath('twisted/internet/error.py')
    outpath = py_compile.compile(error_path, optimize=1)
    replace_in_zip(build_path + '/lib/library.zip', [['twisted/internet/error.pyc', outpath]])


def do_prebuild_patches():
    strptime_patcher()


def do_postbuild_patches():
    twisted_error_patcher()
