import time


def run_cython(source_directories):
    import Cython.Build
    import Cython.Compiler.Options

    Cython.Compiler.Options.docstrings = False
    Cython.Compiler.Options.emit_code_comments = False
    
    import sys
    old_sys_argv = sys.argv[:]
    sys.argv = [sys.argv[0]] + ['build_ext', '--inplace']

    operating_system = 'windows' if sys.platform == 'win32' else 'linux'

    from distutils.core import setup

    start = time.time()
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
                                                        'buildtools/cython_setup.py',
                                                        'buildtools/build_runner.py',
                                                        'buildtools/signature_tools.py',
                                                        'tests',
                                                        'conditions/examples.py',
                                                        'conditions/test_conditions.py',
                                                        'SupremeCommander.py'
                                                    ],
                                               compiler_directives={
                                                   'language_level': '3'
                                               },
                                               nthreads=1,
                                               annotate=False
                                               )
        )

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
