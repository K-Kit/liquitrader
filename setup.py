import os
import pathlib
import sys
import shutil
import datetime
import glob
import time
import py_compile

import requests.certs

from buildtools import cython_setup, monkey_patcher

# ----
# TOGGLE WHAT GETS BUILT HERE
CYTHONIZE_LIQUITRADER = True
BUILD_LIQUITRADER = True
BUILD_VERIFIER = True
BUILD_UPDATER = False
# ----


BUILD_PATH = './build/liquitrader_win/' if sys.platform == 'win32' else './build/liquitrader_linux/'
BUILD_PATH = pathlib.Path(BUILD_PATH).absolute()


def cythonize_liquitrader(target_packages):
    cython_setup.run_cython(['.'] + target_packages)

    for src_dir, dirs, files in os.walk('./liquitrader'):
        dst_dir = src_dir.replace('liquitrader', '', 1)

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)


def rmtree(pth: pathlib.Path):
    for sub in pth.iterdir():
        if sub.is_dir():
            rmtree(sub)
        else:
            sub.unlink()

    while True:
        try:
            pth.rmdir()
            break
        except OSError:  # Folder not yet empty, wait for OS to catch up
            time.sleep(.05)


def copy_requirements():
    gui_path = BUILD_PATH / 'gui'

    if gui_path.exists():
        rmtree(gui_path)

    while True:
        try:
            shutil.copytree(pathlib.Path('LTGUI/build'), gui_path)
            break
        except PermissionError:
            time.sleep(.1)

    if sys.platform == 'win32':
        shutil.copy('build/liquitrader_win/lib/VCRUNTIME140.dll', 'build/liquitrader_win/')

    else:
        # Copy so's
        lib_dir = BUILD_PATH / 'lib/'
        cffi_dir = lib_dir / '.libs_cffi_backend'
        libffi_dll = lib_dir / [_ for _ in os.listdir(lib_dir) if 'libffi' in _][0]

        os.makedirs(cffi_dir, exist_ok=True)

        try:
            shutil.copy2(libffi_dll, cffi_dir)
        except shutil.SameFileError:
            pass

        talib_bin = '/usr/lib/libta_lib.so.0'
        if os.path.isfile(talib_bin):
            try:
                shutil.copy2(talib_bin, BUILD_PATH)
            except shutil.SameFileError:
                pass
        else:
            print('\nWARNING: COULD NOT FIND TALIB BINARY\n')


def rebuild_pyc():
    # Re-build .pyc files that git destroys
    os.makedirs('dependencies/python/py_built', exist_ok=True)

    for source_file in ('_regex_core.py', '_strptime.py'):
        output_name = 'dependencies/python/py_built/' + source_file.split('.')[0] + '.pyc'
        py_compile.compile('dependencies/python/' + source_file, cfile=output_name)


if __name__ == '__main__':
    # Cleanup .pyc caches
    for path in glob.glob('./**/__pycache__', recursive=True):
        path = os.path.abspath(path)

        try:
            shutil.rmtree(os.path.abspath(path))

        except PermissionError:
            print('Warning: __pycache__ cleanup failed due to running Python process')
            print('This probably won\'t cause issues, but you\'ll be sorry if it does!')

    # ----
    TARGET_PACKAGES = ['analyzers', 'conditions', 'config', 'exchanges', 'utils', 'gui']

    if CYTHONIZE_LIQUITRADER:
        cythonize_liquitrader(TARGET_PACKAGES)

    TARGET_DIRECTORIES = ['./' + package for package in TARGET_PACKAGES]
    sys.path.extend(TARGET_DIRECTORIES)

    # rebuild_pyc()

    # Dependencies are automatically detected, but it might need fine tuning || LOL BULLSHIT
    build_options = {
        'build_exe': {
            'build_exe': BUILD_PATH,
            'namespace_packages': ['zope', 'binance'],

            # Remove package paths from tracebacks
            # 'replace_paths': [('*', '/')],

            "includes": [
                'cryptography',
                'binance',
                # 'dev_keys_binance'  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            ],

            'bin_includes': ['openblas', 'libgfortran', 'libffi', 'numpy'],

            'include_files': [('dependencies/liquitrader.ico', 'gui/favicon.ico'),
                              (requests.certs.where(), 'lib/cacert.pem'),
                              ('tos.txt', 'tos.txt'),
                              ('version.txt', 'version.txt'),
                              ],

            'packages': TARGET_PACKAGES + [  # LiquiTrader internal packages
                'os', 'asyncio', 'configparser', 'datetime', 'io', 'json', 'database_models',
                'pkg_resources._vendor',
                'cffi', '_cffi_backend',
                'encodings', 'encodings.cp949', 'encodings.utf_8', 'encodings.ascii',
                'appdirs',
                'cheroot',
                'flask', 'flask_sqlalchemy', 'flask_login', 'flask_bootstrap', 'flask_wtf', 'flask_otp',
                'flask_compress', 'flask_sslify', 'flask_talisman', 'flask_jwt',
                'OpenSSL',
                'scrypt', '_scrypt',
                'arrow', 'dateutil', 'dateutil.tz', 'dateutil.zoneinfo',
                'distro',
                'jinja2',
                'sqlalchemy',
                'pyqrcode',
                'onetimepass',
                'wtforms',
                'requests',
                'numpy', 'numpy.core.numeric', 'numpy.core.multiarray',
                'pandas', 'pandas.core.computation',
                'json_minify',
                'packaging',
                'ccxt',
                'binance',
                'talib',
                'zope', 'zope.interface',
                'regex', 'idna', 'dateparser',
                'lxml', 'lxml._elementpath', 'lxml.etree', 'gzip', 'psutil', 'encodings'
            ],

            'excludes': [
                'tkinter', 'cProfile', 'profile', 'pdb', 'pydoc', 'doctest',
                'Cython', 'zodbpickle',
                'conditions.test_conditions',  # 'dev_keys_binance', !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            ],

            'zip_include_packages': '*',
            'zip_exclude_packages': ['flask_bootstrap', 'dateutil'],

            'include_msvcr': True,
            #'optimize': 2,
        }
    }

    """
    'cheroot.test', 'cheroot.testing',
                         'pyximport',
                         'pandas.conftest', 'pandas.tests', 'pandas.testing', 'pandas.util._test_decorators',
                            'pandas.util._tester', 'pandas.util.testing',
                         'psutil.tests',
                         'numpy.conftest', 'numpy.tests', 'numpy.testing', 'numpy.distutils.tests',  # 'numpy.core.tests.',
                            'numpy.f2py.tests', 'numpy.lib.tests', 'numpy.linalg.tests', 'numpy.ma.tests', 'numpy.matrixlib.tests',
                            'numpy.polynomial.tests',
                         'nose',
                         'sqlalchemy.testing',
                         'talib.test_abstract', 'talib.test_data', 'talib.test_func', 'talib.test_pandas', 'talib.test_stream',
                         'zope.annotation.tests', 'zope.browserpage.tests', 'zope.browserresource.tests',
                            'zope.cachedescriptors.tests', 'zope.component.tests', 'zope.configuration.tests',
                            'zope.container.tests', 'zope.contentprovider.tests', 'zope.contenttype.tests',
                            'zope.deferredimport.tests', 'zope.deprecation.tests', 'zope.dottedname.tests',
                            'zope.event.tests', 'zope.exceptions.tests', 'zope.globalrequest.tests',
                            'zope.i18n.locales.tests', 'zope.i18n.testing', 'zope.i18n.tests', 'zope.i18nmessageid.tests',
                            'zope.interface.common.tests', 'zope.interface.tests', 'zope.lifecycleevent.tests',
                            'zope.location.tests', 'zope.pagetemplate.tests', 'zope.processlifetime.tests',
                            'zope.proxy.tests', 'zope.ptresource.tests', 'zope.publisher.tests', 'zope.schema.tests',
                            'zope.security.tests', 'zope.sequencesort.tests', 'zope.site.tests', 'zope.size.tests',
                            'zope.structuredtext.tests', 'zope.tal.tests', 'zope.tales.tests', 'zope.testbrowser.tests',
                            'zope.testing', 'zope.traversing.tests', 'zope.viewlet.tests',

       'unittest', 'pytest', 'setuptools',
    """

    from cx_Freeze import setup, Executable

    os.makedirs(BUILD_PATH / 'setup', exist_ok=True)
    os.makedirs(BUILD_PATH / 'config', exist_ok=True)  # Where database and config is stored

    if sys.platform == 'win32':
        executables = [Executable('runner.py',
                                  targetName='liquitrader.exe',
                                  icon='dependencies/liquitrader.ico')
                       ]

        build_options['build_exe']['packages'].append('win32api')

        build_options['build_exe']['include_files'].append(('dependencies/vc_redist_installer.exe',
                                                            'setup/vc_redist_installer.exe'))

        build_options['build_exe']['include_files'].append(('dependencies/vc_redist_installer.exe.config',
                                                            'setup/vc_redist_installer.exe.config'))

    else:
        executables = [Executable('runner.py',
                                  targetName='liquitrader',
                                  icon='dependencies/liquitrader.ico')
                       ]

        build_options['build_exe']['include_files'].append(('dependencies/setup.sh', 'setup/setup.sh'))

    # Write library monkey-patches to site-packages
    monkey_patcher.do_prebuild_patches()

    if BUILD_LIQUITRADER:
        print('\n=====\nBuilding LiquiTrader...\n')
        setup(name='liquitrader',
              version='2.0.0',
              description='LiquiTrader',
              options=build_options,
              executables=executables
        )

    if BUILD_UPDATER:
        print('\n=====\nBuilding Updater...\n')
        setup(name='updater',
              version='2.0.0',
              description='LiquiTrader updater',
              executables=[Executable('updater.py')],
              options={
                'build_exe': {
                    'build_exe': BUILD_PATH / 'updater',
                    'packages': ['ctypes', '_ctypes', 'requests', 'idna', 'idna.idnadata', 'psutil'],
                    'include_files': [(requests.certs.where(), 'lib/cacert.pem')],
                    # 'zip_include_packages': '*',
                    # 'zip_exclude_packages': [],

                    'excludes': ['tkinter'],

                    # Remove package paths from tracebacks
                    # 'replace_paths': [('*', '/')],

                    'include_msvcr': True
                }
            }
        )

    # ----
    copy_requirements()

    # Remove map files (for prod)
    try: os.remove(BUILD_PATH / 'static' / 'static' / 'js' / 'main.js.map')
    except FileNotFoundError: pass
    try: os.remove(BUILD_PATH / 'static' / 'static' / 'css' / 'main.css.map')
    except FileNotFoundError: pass

    # ----
    monkey_patcher.do_postbuild_patches()

    # ----
    for file in glob.glob(f'{BUILD_PATH}**/*.py', recursive=True):
        print(f'Compiling {file} to bytecode')
        py_compile.compile(file, optimize=1)
        time.sleep(1)
        os.remove(file)

    # ----
    # Clean up .pyd/.so's alongside .py's leftover from build
    cython_setup.cleanup_pyd()

    # ----
    what_built = 'LiquiTrader' if BUILD_LIQUITRADER else ''
    what_built += ' and ' if BUILD_LIQUITRADER and BUILD_UPDATER else ''
    what_built += 'Updater' if BUILD_UPDATER else ''

    if what_built:
        print(f'\nBuild of {what_built} completed at {datetime.datetime.now().strftime("%I:%M%p on %m/%d (%A)")}')
