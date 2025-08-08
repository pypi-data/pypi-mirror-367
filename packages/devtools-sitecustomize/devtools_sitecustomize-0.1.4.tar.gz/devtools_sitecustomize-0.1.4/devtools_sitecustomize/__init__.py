__version__ = '0.1.4'

import builtins

from devtools import debug


def add_debug_to_builtins():
    """
    This function adds devtools.debug to builtins.
    """
    print(
        '🚀 devtools.debug being added to builtins via devtools-sitecustomize plugin!'
    )
    setattr(builtins, 'debug', debug)
