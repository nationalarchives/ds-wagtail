from .base import *  # noqa: F401

try:
    from .local import *  # noqa: F401
except ImportError:
    pass

SECRET_KEY = "abc123"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "mydatabase",
    }
}

ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Disable birdbath completely when testing
INSTALLED_APPS = INSTALLED_APPS.copy()  # noqa: F405
INSTALLED_APPS.remove("birdbath")

# Allow integration tests to run without needing to collectstatic
# See https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#staticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

IMAGE_VIEWER_REQUIRE_LOGIN = False
RECORD_DETAIL_REQUIRE_LOGIN = False
SEARCH_VIEWS_REQUIRE_LOGIN = False

CLIENT_BASE_URL = "https://kong.test/data"
CLIENT_MEDIA_URL = "https://kong.test/media"

ENVIRONMENT_NAME = "test"
SENTRY_SAMPLE_RATE = 0
