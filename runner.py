#import sys

#if hasattr(sys, 'frozen'):
import utils.runtime_handler

utils.runtime_handler.enable_traceback_hook()  # Enable custom traceback handling (to strip build path info)
utils.runtime_handler.enable_faulthandler()  # Handles crashes that otherwise would be lost


if __name__ == '__main__':
    import liquitrader
    liquitrader.main()
