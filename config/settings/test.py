import os

from .production import *  # noqa: F401, F403
from .production import BASE_DIR, INSTALLED_APPS

ENVIRONMENT_NAME = "test"

DEBUG = True

SECRET_KEY = "abc123"

WAGTAILADMIN_BASE_URL = "http://localhost"
WAGTAILAPI_IMAGES_BASE_URL = "http://localhost"
WAGTAILAPI_MEDIA_BASE_URL = "http://localhost"

ALLOWED_HOSTS = ["*"]

# Disable birdbath completely when testing
INSTALLED_APPS = INSTALLED_APPS.copy()
INSTALLED_APPS.remove("birdbath")

WAGTAIL_2FA_REQUIRED = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

ROSETTA_API_URL = "http://rosetta.test/data"

RECORD_DETAILS_CACHE_TIMEOUT = 0

SENTRY_SAMPLE_RATE = 0

RECORD_DETAILS_CACHE_TIMEOUT = 0
