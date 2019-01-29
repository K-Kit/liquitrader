import os
import sys
import traceback
import faulthandler
# import logging
# from io import StringIO

import arrow


def _flush(message):
    sys.stderr.write(message + '\n')
    sys.stderr.flush()


class _Hook(object):
    def __init__(self,
                 entries,
                 align=False,
                 strip_path=False,
                 conservative=False):
        self.entries = entries
        self.align = align
        self.strip = strip_path
        self.conservative = conservative

    def reverse(self):
        self.entries = self.entries[::-1]

    def rebuild_entry(self, entry):
        entry = list(entry)

        # This is the file path.
        if self.strip:
            path_parts = entry[0].split(os.path.sep)

            py_root = 0
            for i, p in enumerate(path_parts):
                if 'python' in p.lower():
                    py_root = i
                    break

            new_path = os.path.sep.join(path_parts[py_root + 1:])
            entry[0] = new_path.replace(f'lib{os.path.sep}site-packages{os.path.sep}', '').replace('dist-packages/', '')

        # entry[0] = os.path.basename(entry[0]) if self.strip else entry[0]

        # Always an int (entry line number)
        entry[1] = str(entry[1])

        new_entry = [
            entry[1],
            entry[0],
            entry[2],
            entry[3],
        ]

        if self.conservative:
            new_entry[0], new_entry[1] = new_entry[1], new_entry[0]

        return new_entry

    @staticmethod
    def align_all(entries):
        lengths = [0, 0, 0, 0]

        for entry in entries:
            for index, field in enumerate(entry):
                lengths[index] = max(lengths[index], len(str(field)))
        return lengths

    @staticmethod
    def align_entry(entry, lengths):
        return ' '.join(['{0: >{1}}'.format(field, lengths[index]) for index, field in enumerate(entry)])

    def generate_backtrace(self):
        """Return the (potentially) aligned, rebuit traceback

        Yes, we iterate over the entries thrice. We sacrifice
        performance for code readability. I mean.. come on, how long can
        your traceback be that it matters?
        """

        backtrace = []
        for entry in self.entries:
            backtrace.append(self.rebuild_entry(entry))

        # Get the lenght of the longest string for each field of an entry
        lengths = self.align_all(backtrace) if self.align else [1, 1, 1, 1]

        aligned_backtrace = []
        for entry in backtrace:
            if entry is not None:
                aligned_backtrace.append('\t' + self.align_entry(entry, lengths))

        return aligned_backtrace


def enable_traceback_hook(reverse=False,
         align=False,
         strip_path=True,
         conservative=False,
         tb=None,
         tpe=None,
         value=None):

    """Hook the current excepthook to the backtrace.

    If `align` is True, all parts (line numbers, file names, etc..) will be
    aligned to the left according to the longest entry.

    If `strip_path` is True, only the file name will be shown, not its full
    path.

    If `enable_on_envvar_only` is True, only if the environment variable
    `ENABLE_BACKTRACE` is set, backtrace will be activated.

    If `on_tty` is True, backtrace will be activated only if you're running
    in a readl terminal (i.e. not piped, redirected, etc..).

    If `convervative` is True, the traceback will have more seemingly original
    style (There will be no alignment by default, 'File', 'line' and 'in'
    prefixes and will ignore any styling provided by the user.)

    See https://github.com/nir0s/backtrace/blob/master/README.md for
    information on `styles`.
    """

    def backtrace_excepthook(tpe=None, value=None, tb=None):
        # Don't know if we're getting traceback or traceback entries.
        # We'll try to parse a traceback object.

        try:
            traceback_entries = traceback.extract_tb(tb)
        except AttributeError:
            traceback_entries = tb

        parser = _Hook(traceback_entries, align, strip_path, conservative)
        if reverse:
            parser.reverse()

        tpe = tpe if isinstance(tpe, str) else ''

        tb_message = 'Traceback ({0}):'.format('Most recent call last')
        _flush(tb_message)

        backtrace = parser.generate_backtrace()
        if len(tpe) > 0:
            err_message = tpe + ': ' + str(value)
            backtrace.insert(0 if reverse else len(backtrace), err_message)

        for entry in backtrace:
            _flush(entry)

    if tb is not None:
        backtrace_excepthook(tpe=tpe, value=value, tb=tb)
    else:
        sys.excepthook = backtrace_excepthook


"""
def add_custom_print_exception():
    old_print_exception = traceback.print_exception

    def custom_print_exception(etype, value, tb, limit=None, file=None):
        tb_output = StringIO()
        traceback.print_tb(tb, limit, tb_output)
        logger = logging.getLogger('liquitrader_runtime_logger')
        logger.error(tb_output.getvalue())
        tb_output.close()

        old_print_exception(etype, value, tb, limit=None, file=None)

    traceback.print_exception = custom_print_exception
"""


def enable_faulthandler():
    # Handles crashes that otherwise would be lost

    crash_log = open('crash.log', 'r+')

    if crash_log.read(4):
        print('\n--------\n', file=crash_log)
    print(f'Session: {arrow.utcnow().format("YYYY-MM-DD HH:mm UTC")}\n', file=crash_log)

    faulthandler.enable(crash_log, True)
