from .base import *  # noqa: F401

try:
    from .local import *  # noqa: F401
except ImportError:
    pass

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "abc123"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable birdbath completely when testing
INSTALLED_APPS = INSTALLED_APPS.copy()  # noqa: F405
INSTALLED_APPS.remove("birdbath")

# Allow integration tests to run without needing to collectstatic
# See https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#staticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

ROSETTA_API_URL = "https://rosetta.test/data"

ENVIRONMENT_NAME = "test"
SENTRY_SAMPLE_RATE = 0
