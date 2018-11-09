import sys
import time

from distutils.core import setup

import Cython.Build
import Cython.Compiler.Options


def run_cython(source_directories=None, source_file=None):
    Cython.Compiler.Options.docstrings = False
    Cython.Compiler.Options.emit_code_comments = False

    old_sys_argv = sys.argv[:]
    sys.argv = [sys.argv[0]] + ['build_ext']

    operating_system = 'win' if sys.platform == 'win32' else 'linux'

    start = time.time()
    if source_directories is not None:
        for direct in source_directories:
            setup(
                ext_modules=Cython.Build.cythonize('{}/*.py'.format(direct),
                                                   build_dir=f'build/{operating_system}_cython_src/',
                                                   exclude=[
                                                            '__init__.py',
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
                                               build_dir=f'build/{operating_system}_cython_src/',
                                               compiler_directives={
                                                   'language_level': '3'
                                               },
                                               annotate=False
                                               )
        )

    else:
        raise Exception('No file or directory provided to cython_setup.run_cython()')

    print(f'Cython build complete in {time.time() - start}')

    sys.argv = old_sys_argv

    # Copy built files such that they are next to their .py counterparts
    from distutils.dir_util import copy_tree

    path = f'./build/lib.{"win-amd64-3.6" if sys.platform == "win32" else "build/lib.linux-x86_64-3.6"}/'
    copy_tree(path, './')


def cleanup_pyd():
    import os
    import glob

    # Clean up .pyd/.so stragglers leftover from build (shouldn't be any; sanity check)
    files = [path_obj for path_obj in glob.glob('**', recursive=True) if os.path.isfile(path_obj)]
    files = [os.path.abspath(file) for file in files if not file.startswith('build') and (file.endswith('.pyd') or file.endswith('.so'))]

    for file in files:
        os.remove(file)
