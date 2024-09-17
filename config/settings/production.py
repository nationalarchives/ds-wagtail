import os

from .base import *  # noqa: F401

# TODO: Temporary until the static files can be served via S3 or a CDN
# DEBUG = True

# TODO: Ensure that certificates are always checked by the Client API in production
# CLIENT_VERIFY_CERTIFICATES = True

SECRET_KEY = os.getenv("SECRET_KEY", "")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# TODO: Remove later
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
