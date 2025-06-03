import os

from .base import *  # noqa: F401

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "0.25"))

if CACHES:  # noqa: F405
    CACHES["default"]["TIMEOUT"] = int(  # noqa: F405
        os.getenv("CACHE_DEFAULT_TIMEOUT", "60")
    )
