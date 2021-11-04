from .base import *  # noqa: F401

DEBUG = False

try:
    from .local import *  # noqa: F401
except ImportError:
    pass
