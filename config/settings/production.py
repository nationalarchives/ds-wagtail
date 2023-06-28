import os

from .base import *  # noqa: F401

# TODO: Temporary until the static files can be served via S3 or a CDN
DEBUG = True

# Ensure that certificates are always checked by Kong client in production
KONG_CLIENT_VERIFY_CERTIFICATES = True

# TODO: Generate SECRET_KEY
SECRET_KEY = os.getenv("SECRET_KEY", "")
# Need to get the IP of the load balancer or reverse proxy
ALLOWED_HOSTS = ["*"]
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
STATIC_ROOT = "/app/static"

try:
    from .local import *  # noqa: F401
except ImportError:
    pass
