from .base import *  # noqa: F401

DEBUG = False

# Ensure that certificates are always checked by Kong client in production
KONG_CLIENT_VERIFY_CERTIFICATES = True

try:
    from .local import *  # noqa: F401
except ImportError:
    pass
