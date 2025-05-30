import logging
import os

from .base import *  # noqa: F401
from .util import strtobool

# ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

if DEBUG:  # noqa: F405
    from .base import LOGGING

    LOGGING["root"]["level"] = "DEBUG"

if DEBUG and strtobool(os.getenv("DEBUG_TOOLBAR_ENABLED", "False")):  # noqa: F405
    from .base import INSTALLED_APPS, MIDDLEWARE

    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
