from .base import *  # noqa: F401, F403

SECRET_KEY = "abc123"

WAGTAILADMIN_BASE_URL = "https://www.nationalarchives.gov.uk"
WAGTAILAPI_IMAGES_BASE_URL = "https://www.nationalarchives.gov.uk"
WAGTAILAPI_MEDIA_BASE_URL = "https://www.nationalarchives.gov.uk"

ALLOWED_HOSTS = ["*"]

# Disable birdbath completely when testing
INSTALLED_APPS = INSTALLED_APPS.copy()  # noqa: F405
INSTALLED_APPS.remove("birdbath")

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

ROSETTA_API_URL = "https://rosetta.test/data"

RECORD_DETAILS_CACHE_TIMEOUT = 0

ENVIRONMENT_NAME = "test"
SENTRY_SAMPLE_RATE = 0
