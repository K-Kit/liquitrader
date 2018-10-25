import os
import sys
import shutil
import datetime
import glob

from buildtools import cython_setup, build_runner, signature_tools


if __name__ == '__main__':
    TARGET_PACKAGES = ['analyzers', 'conditions', 'config', 'exchanges', 'pairs', 'utils', 'webserver']
    CYTHON_TARGET_DIRECTORIES = ['.'] + TARGET_PACKAGES
    #cython_setup.run_cython(CYTHON_TARGET_DIRECTORIES)


    # Dynamically generate runner.py
    print('Signing files...')
    if not os.path.exists('./buildtools/liquitrader.pem'):
        signature_tools.generate_private_key()

    to_sign = glob.glob('./*.pyd')
    to_sign.extend(glob.glob('./**/*.pyd', recursive=True))
    to_sign.append('webserver/static/main.js')

    build_runner.build_runner(to_sign=to_sign)
    print('')

    import requests.certs
    import py_compile


    # ----
    # TOGGLE WHAT GETS BUILT HERE
    BUILD_LIQUITRADER = True
    BUILD_UPDATER = False
    # ----

    BUILD_PATH = './build/liquitrader_win/' if sys.platform == 'win32' else './build/liquitrader_linux/'

    TARGET_DIRECTORIES = ['./' + package for package in TARGET_PACKAGES]
    sys.path.extend(TARGET_DIRECTORIES)


    PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))

    os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
    os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

    from cx_Freeze import setup, Executable


    # Dependencies are automatically detected, but it might need fine tuning || LOL BULLSHIT
    build_options = {
        'build_exe': {
            'build_exe': BUILD_PATH,
            'namespace_packages': ['zope'],

            # Remove package paths from tracebacks
            # 'replace_paths': [('*', '/')],

            "includes": ['numpy', 'pandas', 'cryptography'],
            'bin_includes': ['openblas', 'libgfortran', 'libffi'],

            'include_files': [('dependencies/vc_redist_installer.exe', 'setup/vc_redist_installer.exe'),
                              ('dependencies/vc_redist_installer.exe.config', 'setup/vc_redist_installer.exe.config'),
                              ('dependencies/python/py_built/_strptime.pyc', 'lib/_strptime.pyc'),
                              ('dependencies/python/py_built/_regex_core.pyc', 'lib/_regex_core.pyc'),
                              ('dependencies/liquitrader.ico', 'webserver/static/favicon.ico'),
                              (requests.certs.where(), 'lib/cacert.pem'),
                              ('tos.txt', 'tos.txt'),
                              ('version.txt', 'version.txt')
                              ],

            'packages': TARGET_PACKAGES + [  # LiquiTrader internal packages
                         'os', 'asyncio', 'configparser', 'datetime', 'io', 'json',
                         'pkg_resources._vendor',
                         'cffi', '_cffi_backend',
                         'encodings', 'encodings.cp949', 'encodings.utf_8', 'encodings.ascii',
                         'appdirs',
                         'cheroot',
                         'flask', 'flask_sqlalchemy', 'flask_login', 'flask_bootstrap', 'flask_wtf', 'flask_otp',
                         'flask_compress', 'flask_sslify',
                         'OpenSSL',
                         'arrow',
                         'jinja2',
                         'sqlalchemy',
                         'pyqrcode',
                         'onetimepass',
                         'wtforms',
                         'requests',
                         'numpy',
                         'pandas',
                         'json_minify',
                         'packaging',
                         'logger',
                         'ccxt', 'binance',
                         'talib',
                         'zope', 'zope.interface',
                         'regex', 'idna', 'dateparser',
                         'lxml', 'lxml._elementpath', 'lxml.etree', 'gzip', 'psutil', 'encodings'
                         ],

            'excludes': ['tkinter'],

            'zip_include_packages': '*',
            'zip_exclude_packages': ['flask_bootstrap'],

            'include_msvcr': True,
        }
    }

    if sys.platform == 'win32':
        executables = [Executable('runner.py',
                                  targetName='liquitrader.exe',
                                  icon='dependencies/liquitrader.ico')
                       ]
        build_options['build_exe']['packages'].append('win32api')

    else:
        executables = [Executable('runner.py',
                                  targetName='liquitrader',
                                  icon='dependencies/liquitrader.ico')
                       ]


    # Re-build .pyc files that git destroys
    os.makedirs('dependencies/python/py_built', exist_ok=True)
    for source_file in ('_regex_core.py', '_strptime.py'):
        output_name = 'dependencies/python/py_built/' + source_file.split('.')[0] + '.pyc'
        py_compile.compile('dependencies/python/' + source_file, cfile=output_name)


    if BUILD_LIQUITRADER:
        print('\n=====\nBuilding LiquiTrader...\n')
        setup(name='liquitrader',
              version='1.0.3',
              description='LiquiTrader',
              options=build_options,
              executables=executables
              )

    if BUILD_UPDATER:
        print('\n=====\nBuilding Updater...\n')
        setup(name='updater',
              version='1.0.0',
              description='LiquiTrader updater',
              executables=[Executable('updater.py')],
              options={
                  'build_exe': {
                      'build_exe': BUILD_PATH + 'updater/',
                      'packages': ['ctypes', '_ctypes', 'requests', 'idna', 'idna.idnadata', 'psutil'],
                      'include_files': [(requests.certs.where(), 'lib/cacert.pem')],
                      'zip_include_packages': '*',
                      'zip_exclude_packages': [],

                      'excludes': ['tkinter'],

                      # Remove package paths from tracebacks
                      # 'replace_paths': [('*', '/')],

                      'include_msvcr': True
                  }
              }
              )

    cython_setup.cleanup_pyd(TARGET_DIRECTORIES)

    try:
        os.remove(BUILD_PATH + 'webserver/static/main.js.map')
    except FileNotFoundError:
        pass

    if sys.platform != 'win32':
        shutil.rmtree(BUILD_PATH + 'setup', ignore_errors=True)
        os.mkdir(BUILD_PATH + 'setup')
        shutil.copy('dependencies/setup.sh', BUILD_PATH + 'setup/')

    # Copy dll's/so's
    lib_dir = BUILD_PATH + 'lib/'

    if sys.platform != 'win32':
        cffi_dir = lib_dir + '.libs_cffi_backend/'
        libffi_dll = lib_dir + [_ for _ in os.listdir(lib_dir) if 'libffi' in _][0]

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

    what_built = 'LiquiTrader' if BUILD_LIQUITRADER else ''
    what_built += ' and ' if BUILD_LIQUITRADER and BUILD_UPDATER else ''
    what_built += 'Updater' if BUILD_UPDATER else ''

    print(f'\nBuild of {what_built} completed at {datetime.datetime.now().strftime("%I:%M%p on %m/%d (%A)")}')
