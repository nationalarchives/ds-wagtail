import os

from .production import *  # noqa: F401, F403
from .util import strtobool

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

try:
    CACHES["default"]["TIMEOUT"] = int(  # noqa: F405
        os.getenv("CACHE_DEFAULT_TIMEOUT", "1")
    )
except NameError:
    pass


def show_toolbar(request):
    return True


if DEBUG and strtobool(os.getenv("DEBUG_TOOLBAR_ENABLED", "False")):  # noqa: F405
    from .production import INSTALLED_APPS, MIDDLEWARE

    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": "config.settings.develop.show_toolbar",
        "RESULTS_CACHE_SIZE": 50,
    }
