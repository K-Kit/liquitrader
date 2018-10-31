import sys
import time

from distutils.core import setup

import Cython.Build
import Cython.Compiler.Options


def run_cython(source_directories=None, source_file=None):
    Cython.Compiler.Options.docstrings = False
    Cython.Compiler.Options.emit_code_comments = False

    old_sys_argv = sys.argv[:]
    sys.argv = [sys.argv[0]] + ['build_ext', '--inplace']

    operating_system = 'windows' if sys.platform == 'win32' else 'linux'

    start = time.time()
    if source_directories is not None:
        for direct in source_directories:
            setup(
                ext_modules=Cython.Build.cythonize('{}/*.py'.format(direct),
                                                   build_dir=f'./build/cython/{operating_system}/',
                                                   exclude=[
                                                            '{}/__init__.py'.format(direct),
                                                            'runner.py',
                                                            'setup.py',
                                                            'dev_keys_binance.py',
                                                            'buildtools',
                                                            'tests',
                                                            'conditions/examples.py',
                                                            'conditions/test_conditions.py',
                                                            'SupremeCommander.py'
                                                        ],
                                                   compiler_directives={
                                                       'language_level': '3'
                                                   },
                                                   annotate=False
                                                   )
            )

    elif source_file is not None:
        setup(
            ext_modules=Cython.Build.cythonize(source_file,
                                               build_dir=f'./build/cython/{operating_system}/',
                                               compiler_directives={
                                                   'language_level': '3'
                                               },
                                               nthreads=1,
                                               annotate=False
                                               )
        )

    else:
        raise Exception('No file or directory provided to cython_setup.run_cython()')

    print(f'Cython build complete in {time.time() - start}')

    sys.argv = old_sys_argv


def cleanup_pyd(source_directories):
    import glob
    import os
    import sys
    
    ext = 'pyd' if sys.platform == 'win32' else 'so'
    
    for dir in source_directories:
        for pydfile in glob.glob('{}/*.{}'.format(dir, ext)):
            os.remove(pydfile)
