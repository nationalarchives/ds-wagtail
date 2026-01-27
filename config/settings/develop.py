import os

from .production import *  # noqa: F401, F403
from .util import strtobool

DEBUG = strtobool(os.getenv("DEBUG", "False"))

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

try:
    CACHES["default"]["TIMEOUT"] = int(  # noqa: F405
        os.getenv("CACHE_DEFAULT_TIMEOUT", "1")
    )
except NameError:
    pass


def show_toolbar(request):
    return True


if DEBUG:
    LOGGING["root"]["level"] = "DEBUG"  # noqa: F405

    try:
        import debug_toolbar  # noqa: F401

        INSTALLED_APPS += [  # noqa: F405
            "debug_toolbar",
        ]

        MIDDLEWARE = [
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ] + MIDDLEWARE  # noqa: F405

        DEBUG_TOOLBAR_CONFIG = {
            "SHOW_COLLAPSED": True,
        }
    except ImportError:
        pass
