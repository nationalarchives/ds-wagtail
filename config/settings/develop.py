import os

from tna_utilities import strtobool

from .production import *

DEBUG = strtobool(os.getenv("DEBUG", "False"))

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

try:
    CACHES["default"]["TIMEOUT"] = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "1"))
except NameError:
    pass


def show_toolbar(request):
    return True


if DEBUG:
    LOGGING["root"]["level"] = "DEBUG"

    try:
        import debug_toolbar  # noqa: F401

        INSTALLED_APPS += [
            "debug_toolbar",
        ]

        MIDDLEWARE = [
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ] + MIDDLEWARE

        DEBUG_TOOLBAR_CONFIG = {
            "SHOW_COLLAPSED": True,
            "SHOW_TOOLBAR_CALLBACK": "config.settings.develop.show_toolbar",
        }
    except ImportError:
        pass
