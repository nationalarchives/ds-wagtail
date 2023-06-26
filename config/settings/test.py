from .base import *  # noqa: F401

try:
    from .local import *  # noqa: F401
except ImportError:
    pass

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "@6gce61jt^(pyj5+l**&*_#zyxfj5v1*71cs5yoetg-!fsz826"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

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

IMAGE_VIEWER_REQUIRE_LOGIN = False
RECORD_DETAIL_REQUIRE_LOGIN = False
SEARCH_VIEWS_REQUIRE_LOGIN = False

KONG_CLIENT_BASE_URL = "https://kong.test"
