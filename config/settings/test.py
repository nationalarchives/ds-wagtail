from .base import *  # noqa: F401

<<<<<<< HEAD
try:
    from .local import *  # noqa: F401
except ImportError:
    pass
=======
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
>>>>>>> 41f0903 (DF-261:Fix test - make seperate from dev)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "@6gce61jt^(pyj5+l**&*_#zyxfj5v1*71cs5yoetg-!fsz826"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

BIRDBATH_REQUIRED = False

# Allow integration tests to run without needing to collectstatic
# See https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#staticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
