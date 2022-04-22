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
<<<<<<< HEAD

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
=======
>>>>>>> 9a7b66bba974cb9308c54c9d99ba4acd3194add4

BIRDBATH_REQUIRED = False

# Allow integration tests to run without needing to collectstatic
# See https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#staticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
