import os

from platformshconfig import Config
from platformshconfig.config import (
    BuildTimeVariableAccessException,
    NotValidPlatformException,
)

from .base import *  # noqa: F401

config = Config()

SECRET_KEY = config.projectEntropy

MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # noqa: F405
MEDIA_URL = "/media/"

try:
    ALLOWED_HOSTS = ["*"]
except BuildTimeVariableAccessException:
    # Routes aren't available during build-time. Unfortunately, this file needs
    # to be accessed during collectstatic
    pass


# Database (PostgreSQL)
#
# https://docs.platform.sh/configuration/services/postgresql.html
try:
    database_config = config.credentials("db")
except BuildTimeVariableAccessException:
    # Relationships aren't available during build-time. Unfortunately, this
    # file needs to be accessed during collectstatic
    database_config = None

if database_config:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": database_config["path"],
            "USER": database_config["username"],
            "PASSWORD": database_config["password"],
            "HOST": database_config["host"],
            "PORT": database_config["port"],
            "CONN_MAX_AGE": 600,
        }
    }

# Redis
#
# https://docs.platform.sh/configuration/services/redis.html

try:
    redis_config = config.credentials("redis")
except BuildTimeVariableAccessException:
    # Relationships aren't available during build-time. Unfortunately, this
    # file needs to be accessed during collectstatic
    redis_config = None

if redis_config:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"{redis_config['scheme']}://{redis_config['host']}:{redis_config['port']}",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        },
        "renditions": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"{redis_config['scheme']}://{redis_config['host']}:{redis_config['port']}",
            "KEY_PREFIX": "renditions",
        },
    }

# Email
#
# https://docs.platform.sh/administration/web/email.html

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

try:
    email_host = config.smtpHost
except (BuildTimeVariableAccessException, NotValidPlatformException):
    # Relationships aren't available during build-time. Unfortunately, this
    # file needs to be accessed during collectstatic
    # NotValidPlatformException raised if outgoing emails are disabled
    email_host = None

if email_host:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = email_host
