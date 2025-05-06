import logging
import os

from .base import *  # noqa: F401
from .util import strtobool

DEBUG = strtobool(os.getenv("DEBUG", "True"))
DEBUG_TOOLBAR_ENABLED = strtobool(os.getenv("DEBUG_TOOLBAR_ENABLED", "False"))

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

FEATURE_COOKIE_BANNER_ENABLED = strtobool(
    os.getenv("FEATURE_COOKIE_BANNER_ENABLED", "True")
)
COOKIE_DOMAIN = "localhost"

# Silence noisy localization messages/warnings when initializing faker
logging.getLogger("faker").setLevel(logging.ERROR)

try:
    from .local import *  # noqa: F401
except ImportError:
    pass

if DEBUG:
    from .base import LOGGING

    LOGGING["root"]["level"] = "DEBUG"

if DEBUG and DEBUG_TOOLBAR_ENABLED:
    from .base import INSTALLED_APPS, MIDDLEWARE

    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
