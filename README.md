# TNA Wagtail CMS

## Quickstart

```sh
# Build and start the containers
docker compose up -d
```

Log in to the Wagtail Admin on [localhost:8000/admin](http://localhost:8000/admin) with the credentials:

- Username: `admin`
- Password: `admin`

### Pull data from AWS

To [pull example data from AWS](./docs/development/fetching-data.md) from the development environment, install and set up the [AWS CLI](https://aws.amazon.com/cli/) and then run:

```sh
# Log into AWS
aws sso login

# Pull data and media
./dev/pull
```

If you need to inspect the files in S3, open the [S3 Ninja UI](http://localhost:8002/ui).

## Project documentation

This project contains technical documentation written in Markdown in the `/docs` folder. The latest build from the working branch can be viewed online at [nationalarchives.github.io/ds-wagtail](https://nationalarchives.github.io/ds-wagtail/).

You can also view it locally on http://localhost:8001/ which is served from the `docs` container.

## Environment variables

In addition to the [base Docker image variables](https://github.com/nationalarchives/docker/blob/main/docker/tna-python/README.md#environment-variables), this application has support for:

| Variable                             | Purpose                                                                   | Default                                                 |
| ------------------------------------ | ------------------------------------------------------------------------- | ------------------------------------------------------- |
| `ALLOWED_HOSTS`                      | Comma-separated list of allowed Django hosts                              | `""`                                                    |
| `BUILD_VERSION`                      | Build/version identifier surfaced in the app                              | `""`                                                    |
| `CACHE_DEFAULT_TIMEOUT`              | Default cache timeout (only when `REDIS_URL` is set)                      | production: `900`, staging: `60`, develop: `1`          |
| `CSRF_TRUSTED_ORIGINS`               | Comma-separated CSRF trusted origins                                      | `https://www.nationalarchives.gov.uk`                   |
| `DATABASE_ENGINE`                    | Django database backend engine                                            | `django.db.backends.postgresql`                         |
| `DATABASE_HOST`                      | Database host                                                             | _none_                                                  |
| `DATABASE_NAME`                      | Database name                                                             | _none_                                                  |
| `DATABASE_PASSWORD`                  | Database password                                                         | _none_                                                  |
| `DATABASE_PORT`                      | Database port                                                             | `5432`                                                  |
| `DATABASE_USER`                      | Database user                                                             | _none_                                                  |
| `DEBUG`                              | Enable Django debug mode                                                  | production: `False`, staging: `False`, develop: `False` |
| `DEFAULT_FROM_EMAIL`                 | Default sender address for outgoing email                                 | `wagtail@nationalarchives.gov.uk`                       |
| `EMAIL_HOST`                         | SMTP host                                                                 | _none_                                                  |
| `EMAIL_HOST_PASSWORD`                | SMTP password                                                             | _none_                                                  |
| `EMAIL_HOST_USER`                    | SMTP username                                                             | _none_                                                  |
| `EMAIL_PORT`                         | SMTP port                                                                 | `587`                                                   |
| `EMAIL_USE_TLS`                      | Use TLS for SMTP                                                          | `True`                                                  |
| `ENVIRONMENT_NAME`                   | Environment label used in UI/email text                                   | `production`                                            |
| `FRONTEND_CACHE_AWS_DISTRIBUTION_ID` | CloudFront distribution id for Wagtail frontend cache invalidation        | `""`                                                    |
| `LOG_LEVEL`                          | Root logger level                                                         | `warning`                                               |
| `MEDIA_PAGE_URL`                     | Base URL used for live media page links                                   | `""`                                                    |
| `NEW_LABEL_DISPLAY_FOR_DAYS`         | Number of days to show "new" labels                                       | `21`                                                    |
| `RECORD_DETAILS_CACHE_TIMEOUT`       | Record details cache timeout (seconds)                                    | `2592000`                                               |
| `REDIS_URL`                          | Redis connection URL to enable caching                                    | _none_                                                  |
| `ROSETTA_API_URL`                    | Base URL for the CIIM/Rosetta API client                                  | _none_                                                  |
| `SECRET_KEY`                         | Django secret key (required)                                              | _none_                                                  |
| `SENTRY_DSN`                         | Sentry DSN                                                                | `""`                                                    |
| `SENTRY_SAMPLE_RATE`                 | Trace/profile sampling rate                                               | production: `0.1`, staging: `0.25`, develop: `1.0`      |
| `USE_X_FORWARDED_HOST`               | Trust `X-Forwarded-Host` header                                           | `False`                                                 |
| `WAGTAILADMIN_BASE_URL`              | Public base URL for Wagtail admin                                         | `""`                                                    |
| `WAGTAILAPI_AUTHENTICATION`          | Enable authentication on Wagtail API                                      | `True`                                                  |
| `WAGTAILAPI_BASE_URL`                | Public base URL for Wagtail API                                           | `WAGTAILADMIN_BASE_URL`                                 |
| `WAGTAILAPI_LIMIT_MAX`               | Max results allowed in Wagtail API response via `?limit=` (0 = unlimited) | `0`                                                     |
| `WAGTAIL_2FA_REQUIRED`               | Require 2FA for Wagtail admin users                                       | `True`                                                  |
| `WAGTAIL_AUTOSAVE_INTERVAL`          | Wagtail editor autosave interval in ms (`0` disables autosave)            | `0`                                                     |
| `WAGTAIL_HEADLESS_PREVIEW_URL`       | Headless preview URL template                                             | `{SITE_ROOT_URL}/preview/`                              |
| `AWS_STORAGE_BUCKET_NAME`            | The name of the bucket where the Wagtail media files are kept             | _none_                                                  |
| `AWS_S3_ACCESS_KEY_ID`               | The AWS Access Key ID                                                     | _none_                                                  |
| `AWS_S3_SECRET_ACCESS_KEY`           | The AWS Secret Access Key                                                 | _none_                                                  |
| `AWS_S3_ENDPOINT_URL`                | A custom S3 endpoint                                                      | _none_                                                  |
| `AWS_S3_REGION_NAME`                 | The AWS region for the S3 bucket                                          | `eu-west-2`                                             |
| `AWS_S3_URL_PROTOCOL`                | The protocol to use when generating links to media files                  | `https`                                                 |
| `AWS_S3_CUSTOM_DOMAIN`               | The domain to use when generating links to media files                    | `{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com`            |
