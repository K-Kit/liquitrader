import py_compile
import os
import sys
import shutil
import datetime
import glob

import requests.certs

from buildtools import cython_setup, build_verifier, signature_tools, monkey_patcher


if __name__ == '__main__':
    # ----
    # TOGGLE WHAT GETS BUILT HERE
    CYTHONIZE_LIQUITRADER = True
    BUILD_LIQUITRADER = True
    BUILD_UPDATER = False
    # ----

    TARGET_PACKAGES = ['analyzers', 'conditions', 'config', 'exchanges', 'pairs', 'utils', 'gui']

    internal_lib_copy_dests = []
    if CYTHONIZE_LIQUITRADER:
        # Write out placeholder verifier
        with open('strategic_analysis.py', 'w') as f:
            f.write('def verify(): pass\n')

        CYTHON_TARGET_DIRECTORIES = ['.'] + TARGET_PACKAGES
        cython_setup.run_cython(CYTHON_TARGET_DIRECTORIES)

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

                internal_lib_copy_dests.append(dst_file)

    BUILD_PATH = './build/liquitrader_win/' if sys.platform == 'win32' else './build/liquitrader_linux/'

    TARGET_DIRECTORIES = ['./' + package for package in TARGET_PACKAGES]
    sys.path.extend(TARGET_DIRECTORIES)

    from cx_Freeze import setup, Executable


    # # Re-build .pyc files that git destroys
    # os.makedirs('dependencies/python/py_built', exist_ok=True)
    # for source_file in ('_regex_core.py', '_strptime.py'):
    #     output_name = 'dependencies/python/py_built/' + source_file.split('.')[0] + '.pyc'
    #     py_compile.compile('dependencies/python/' + source_file, cfile=output_name)


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
                'TimeSyncWin', 'strategic_analysis',
                'dev_keys_binance'  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            ],

            'bin_includes': ['openblas', 'libgfortran', 'libffi'],

            'include_files': [('dependencies/vc_redist_installer.exe', 'setup/vc_redist_installer.exe'),
                              ('dependencies/vc_redist_installer.exe.config', 'setup/vc_redist_installer.exe.config'),
                              ('dependencies/liquitrader.ico', 'webserver/static/favicon.ico'),
                              (requests.certs.where(), 'lib/cacert.pem'),
                            #   ('dependencies/python/py_built/_strptime.pyc', 'lib/_strptime.pyc'),
                              ('tos.txt', 'tos.txt'),
                              ('version.txt', 'version.txt'),
                              ('config/BuyStrategies.json', 'config/BuyStrategies.json'),
                              ('config/DCABuyStrategies.json', 'config/DCABuyStrategies.json'),
                              ('config/GeneralSettings.json', 'config/GeneralSettings.json'),
                              ('config/GlobalTradeConditions.json', 'config/GlobalTradeConditions.json'),
                              ('config/PairSpecificSettings.json', 'config/PairSpecificSettings.json'),
                              ('config/SellStrategies.json', 'config/SellStrategies.json')
                              ],

            'packages': TARGET_PACKAGES + [  # LiquiTrader internal packages
                         'os', 'asyncio', 'configparser', 'datetime', 'io', 'json',
                         'pkg_resources._vendor',
                         'cffi', '_cffi_backend',
                         'encodings', 'encodings.cp949', 'encodings.utf_8', 'encodings.ascii',
                         'appdirs',
                         'cheroot',
                         'flask', 'flask_sqlalchemy', 'flask_login', 'flask_bootstrap', 'flask_wtf', 'flask_otp',
                            'flask_compress', 'flask_sslify', 'flask_cors',
                         'OpenSSL',
                         'arrow',
                         'jinja2',
                         'sqlalchemy',
                         'pyqrcode',
                         'onetimepass',
                         'wtforms',
                         'requests',
                         'numpy', 'numpy.core.numeric',
                         'pandas',
                         'json_minify',
                         'packaging',
                         'logger',
                         'ccxt',
                         'binance',
                         'talib',
                         'zope', 'zope.interface',
                         'regex', 'idna', 'dateparser',
                         'lxml', 'lxml._elementpath', 'lxml.etree', 'gzip', 'psutil', 'encodings'
                         ],

            'excludes': [
                         'tkinter', 'cProfile', 'profile', 'pdb', 'pydoc', 'doctest',
                         'Cython',
                         'conditions.test_conditions', # 'dev_keys_binance', !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                         ],

            'zip_include_packages': '*',
            'zip_exclude_packages': ['flask_bootstrap'],

            'include_msvcr': True,
            'optimize': 2,
        }
    }

    """
    'cheroot.test', 'cheroot.testing',
                         'cython', 'pyximport',
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
                            
        'tkinter', 'unittest', 'mock', 'pytest', 'pdb', 'doctest', 'cProfile', 'profile',
                            'distutils', 'setuptools',
    """

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

    # Write library monkey-patches to site-packages
    monkey_patcher.do_patches()

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
                      #'zip_include_packages': '*',
                      #'zip_exclude_packages': [],

                      'excludes': ['tkinter'],

                      # Remove package paths from tracebacks
                      # 'replace_paths': [('*', '/')],

                      'include_msvcr': True
                  }
              }
              )

    # Clean up copied .pyd/.so
    if CYTHONIZE_LIQUITRADER:
        for file in internal_lib_copy_dests:
            os.remove(file)

    if sys.platform == 'win32':
        shutil.copy('build/liquitrader_win/lib/VCRUNTIME140.dll', 'build/liquitrader_win/')

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

    # ----
    # Dynamically generate verifier.py and build into package
    
    opsys = 'win' if sys.platform == 'win32' else 'linux'
    exe_ext = '.exe' if opsys == 'win' else ''

    # # Delete the old build files
    # try: os.remove(f'build/cython/{opsys}/strategic_analysis.c')
    # except FileNotFoundError: pass
    # try: os.remove(f'build/temp.linux-x86_64-3.6/build/cython/{opsys}/strategic_analysis.o')
    # except FileNotFoundError: pass
    # try: os.remove('liquitrader/strategic_analysis.pyd')
    # except FileNotFoundError: pass

    print('Signing files...')
    if not os.path.exists('./buildtools/liquitrader.pem'):
        signature_tools.generate_private_key()

    exclude = ['strategic_analysis']
    exclude_ext = ['.txt', '.json', '.sqlite', '.ini', '.cfg']
    to_sign = []
    for file in glob.glob(f'./build/liquitrader_{opsys}/**/*.*', recursive=True):
        bad = False

        for ext in exclude_ext:
            if file.endswith(ext):
                bad = True
                break

        for exclu in exclude:
            if bad or exclu in file:
                bad = True
                break

        if not bad:
            to_sign.append(file)

    build_verifier.build_verifier(to_sign=to_sign)

    #try: os.remove('__init__.py')
    #except FileNotFoundError: pass
    cython_setup.run_cython(source_file='./strategic_analysis.py')
    #with open('__init__.py', 'w') as f: pass  # touch __init__.py

    try:
        new_verifier = glob.glob(f'./liquitrader/strategic_analysis*')[0]
    except IndexError:
        new_verifier = glob.glob(f'./strategic_analysis.*.*')[0]

    verifier_fname = new_verifier.replace(os.path.sep, '/').split('/')[-1]
    shutil.copyfile(new_verifier, f'./build/liquitrader_{opsys}/lib/{verifier_fname}')

    # ----
    what_built = 'LiquiTrader' if BUILD_LIQUITRADER else ''
    what_built += ' and ' if BUILD_LIQUITRADER and BUILD_UPDATER else ''
    what_built += 'Updater' if BUILD_UPDATER else ''

    if what_built:
        print(f'\nBuild of {what_built} completed at {datetime.datetime.now().strftime("%I:%M%p on %m/%d (%A)")}')
