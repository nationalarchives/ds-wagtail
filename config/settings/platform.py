from .base import *

from platformshconfig import Config
from platformshconfig.config import (
    BuildTimeVariableAccessException,
    NotValidPlatformException,
)
from urllib.parse import urlparse


config = Config()

SECRET_KEY = config.projectEntropy

try:
    ALLOWED_HOSTS = [urlparse(url).netloc for url in config.get_upstream_routes().keys()]
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


# Elasticsearch
#
# https://docs.platform.sh/configuration/services/elasticsearch.html
try:
    search_config = config.credentials("elasticsearch")
except BuildTimeVariableAccessException:
    # Relationships aren't available during build-time. Unfortunately, this
    # file needs to be accessed during collectstatic
    search_config = None

if search_config:
    WAGTAILSEARCH_BACKENDS = {
        "default": {
            "BACKEND": "wagtail.search.backends.elasticsearch7",
            "URLS": [
                f"{search_config['scheme']}://{search_config['username']}:{search_config['password']}@{search_config['host']}:{search_config['port']}"
            ],
            "INDEX": "wagtail",
            "TIMEOUT": 5,
            "OPTIONS": {},
            "INDEX_SETTINGS": {},
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
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f"{redis_config['scheme']}://{redis_config['host']}:{redis_config['port']}",
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
        },
        'renditions': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f"{redis_config['scheme']}://{redis_config['host']}:{redis_config['port']}",
            'KEY_PREFIX': 'renditions',
        }
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


# Static files
#
# https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#django.contrib.staticfiles.storage.ManifestStaticFilesStorage

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
