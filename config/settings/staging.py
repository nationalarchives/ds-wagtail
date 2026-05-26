import os

from tna_utilities import strtobool

from .production import *

DEBUG = strtobool(os.getenv("DEBUG", "False"))

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "0.25"))

try:
    CACHES["default"]["TIMEOUT"] = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "60"))
except NameError:
    pass
