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

ROSETTA_API_URL = "https://rosetta.test/data"

ENVIRONMENT_NAME = "test"
SENTRY_SAMPLE_RATE = 0
