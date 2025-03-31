import os

from .base import *  # noqa: F401

# TODO: Can we get away without whitenoise?
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# TODO: Remove later
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "0.25"))
