import os

from .base import *  # noqa: F401
from .util import strtobool

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

CACHES["default"]["TIMEOUT"] = int(  # noqa: F405
    os.getenv("CACHE_DEFAULT_TIMEOUT", "1")
)

if DEBUG and strtobool(os.getenv("DEBUG_TOOLBAR_ENABLED", "False")):  # noqa: F405
    from .base import INSTALLED_APPS, MIDDLEWARE

    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
