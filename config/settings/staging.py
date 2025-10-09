import os

from .production import *  # noqa: F401, F403

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "0.25"))

try:
    CACHES["default"]["TIMEOUT"] = int(  # noqa: F405
        os.getenv("CACHE_DEFAULT_TIMEOUT", "60")
    )
except NameError:
    pass
