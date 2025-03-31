# Configuring an environment

Most app configuration is controlled via **env** vars, which are managed from the 'Configuration' panel in AWS.

To understand the full range of supported env vars and how they correlate to Django project configuration, take a good look through `config/base.py`.

NOTE: The `Dockerfile` included in project sets a few 'higher order' env vars for the container to use too (using the `ENV` statement). The `DJANGO_SETTINGS_MODULE` one is particularly important: Without it, the app will attempt to run with `dev` settings, which are intended for local development only.

The env vars you'll definitely want to set for each environment are:

## 1. The basics:

### `SECRET_KEY`

**This must be a large random value and it must be kept secret.**

Each environment should have a unique value. Particular care should be taken to ensure that the key used in production isn’t used anywhere else.

### `DATABASE_URL`

Postgres connection string including the user, password, host, port and target database name in a single string,

e.g: **postgres://USER:PASSWORD@HOST:PORT/DB_NAME**

NOTE: The database 'DB_NAME' must already exist, but can be empty. The app will create any database tables / indexes it needs.

### `PRIMARY_HOST`

The primary domain that will be used to access the Wagtail CMS for this environment.

e.g. **eta.nationalarchives.gov.uk**.

## 2. Redis (for internal caching)

### `REDIS_TLS_URL`

Connection string for a TLS-enabled Redis instance.

e.g. **rediss://USER:PASSWORD@HOST:PORT/DB_NAME**

### `REDIS_URL`

Connection string for a Redis instance without TLS enabled.

e.g. **redis://USER:PASSWORD@HOST:PORT/DB_NAME**

## 3. Email (SMTP)

### `SERVER_EMAIL`

Default: **'root@localhost'**

The 'from' address that should be used for emails sent by the server to site admins and other users.

### `EMAIL_HOST`

Default: **'localhost'**

The host to use for sending email.

### `EMAIL_PORT`

Default: **25**

Port to use for the SMTP server defined in `EMAIL_HOST`.

### `EMAIL_HOST_USER`

Default: **''** (empty string)

Username to use for the SMTP server defined in `EMAIL_HOST`. If empty, Django won’t attempt authentication.

### `EMAIL_HOST_PASSWORD`

Default: **''** (Empty string)

Password to use for the SMTP server defined in `EMAIL_HOST`. This setting is used in conjunction with `EMAIL_HOST_USER` when authenticating to the SMTP server. If either of these settings is empty, Django won’t attempt authentication.

### `EMAIL_USE_TLS`

Default: **False**

Whether to use a TLS (secure) connection when talking to the SMTP server. This is used for explicit TLS connections, generally on port 587. If you are experiencing hanging connections, see the implicit TLS setting `EMAIL_USE_SSL`.

### `EMAIL_USE_SSL`

Default: **False**

Whether to use an implicit TLS (secure) connection when talking to the SMTP server. In most email documentation this type of TLS connection is referred to as SSL. It is generally used on port 465. If you are experiencing problems, see the explicit TLS setting `EMAIL_USE_TLS`.

NOTE: `EMAIL_USE_TLS` and `EMAIL_USE_SSL` are mutually exclusive, so only set one of those settings to `True`.

## 4. Sentry (Error logging and performance monitoring)

Below are the key env vars used to configure Sentry for each environment. See [Sentry's official guide](https://docs.sentry.io/platforms/python/guides/django/) for further information on configuring Sentry for Django projects.

### `SENTRY_DSN`

Default: `None`

The project-specific identifier provided by Sentry. This value should remain the same accross all environments... the `ENVIRONMENT_NAME` env var value is used to differentiate between environments.

### `ENVIRONMENT_NAME`

Default: `production`

A string used to populate the `environment` value on issues and other transactions sent to Sentry from this environment. In the Sentry UI, this value can be used as a filter, allowing you to easily see which issues apply to which environment.

### `SENTRY_SAMPLE_RATE`

Default: 0.5

A number between `0.0` and `1.0`, which determines how many processes out of all processes should be tracked/analysed in order to send performance data to Sentry. A value of `0.0` means that no processes should be tracked, and a value of `1.0` mean that ALL should be tracked.

Performance monitoring has a minimal impact on app performance, but even so, Sentry recommend using a value less than `1.0` in production (hence using `0.5` as the default).

### `SENTY_SEND_USER_DATA`

Default: `False`

This value determines whether data about the 'currently-logged in user' is included in the error reports sent to Sentry. This can be useful in 'testing' environments, as it can help developers to see which tester is having the problem. However, in production, we need to be far more careful leaking personal data - therefore, this option should be turned off in that environment (hence setting `False` as the default).
