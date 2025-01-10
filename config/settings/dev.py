import logging
import os

from .base import *  # noqa: F401
from .util import strtobool

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = strtobool(os.getenv("DEBUG", "True"))  # noqa: F405
DEBUG_TOOLBAR_ENABLED = strtobool(  # noqa: F405
    os.getenv("DEBUG_TOOLBAR_ENABLED", "False")  # noqa: F405
)

WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL", "http://localhost:8000")
WAGTAIL_HEADLESS_PREVIEW = {
    "CLIENT_URLS": {
        "default": os.getenv(
            "WAGTAILADMIN_HEADLESS_PREVIEW_URL",
            "http://localhost:65535/preview",
        ),
    },
    "SERVE_BASE_URL": os.getenv(
        "WAGTAILADMIN_HEADLESS_BASE_URL", "http://localhost:65535"
    ),
    "REDIRECT_ON_PREVIEW": strtobool(
        os.getenv("WAGTAILADMIN_HEADLESS_REDIRECT_ON_PREVIEW", "False")
    ),
    "ENFORCE_TRAILING_SLASH": strtobool(
        os.getenv("WAGTAILADMIN_HEADLESS_ENFORCE_TRAILING_SLASH", "True")
    ),
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "abc123"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

IMAGE_VIEWER_REQUIRE_LOGIN = False
RECORD_DETAIL_REQUIRE_LOGIN = False
SEARCH_VIEWS_REQUIRE_LOGIN = False
FEATURE_BETA_BANNER_ENABLED = strtobool(
    os.getenv("FEATURE_BETA_BANNER_ENABLED", "True")
)
FEATURE_COOKIE_BANNER_ENABLED = strtobool(
    os.getenv("FEATURE_COOKIE_BANNER_ENABLED", "True")
)
FEATURE_FEEDBACK_MECHANISM_ENABLED = strtobool(
    os.getenv("FEATURE_FEEDBACK_MECHANISM_ENABLED", "True")
)
DJANGO_SERVE_STATIC = strtobool(os.getenv("DJANGO_SERVE_STATIC", "True"))
COOKIE_DOMAIN = "localhost"

MEDIA_ROOT = "/media"

# Silence noisy localization messages/warnings when initializing faker
logging.getLogger("faker").setLevel(logging.ERROR)

try:
    from .local import *  # noqa: F401
except ImportError:
    pass

if DEBUG:
    from .base import LOGGING

    LOGGING["root"]["level"] = "DEBUG"

if not DEBUG and DJANGO_SERVE_STATIC:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

if DEBUG and DEBUG_TOOLBAR_ENABLED:
    from .base import INSTALLED_APPS, MIDDLEWARE

    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

    def show_toolbar(request) -> bool:
        return strtobool(os.getenv("DEBUG_TOOLBAR", "False"))

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    }

MIDDLEWARE += ["config.middleware.CorsMiddleware"]  # noqa: F405
