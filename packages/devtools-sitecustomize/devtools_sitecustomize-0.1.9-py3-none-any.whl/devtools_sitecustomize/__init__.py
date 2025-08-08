__version__ = '0.1.9'

import builtins

from devtools import debug


def add_debug_to_builtins():
    setattr(builtins, 'debug', debug)
