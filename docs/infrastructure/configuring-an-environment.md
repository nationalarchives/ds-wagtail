# Configuring an environment

Most app configuration is controlled via environment variables.

## Where to configure values

- For local development, values are set in `docker-compose.yml` and `.env`.
- For deployed environments, values are managed in `ds-infrastructure-web`.

For the full, maintained variable table and defaults, see [README.md](https://github.com/nationalarchives/ds-wagtail?tab=readme-ov-file#environment-variables).

## How settings modules are selected

- The Docker image defaults `DJANGO_SETTINGS_MODULE` to `config.settings.production`.
- Local `docker-compose.yml` overrides this to `config.settings.develop`.

The settings modules are in `config/settings/` and `develop`/`staging` inherit from `production`.

## Minimum required variables

At minimum, each environment should provide:

- `SECRET_KEY` (required and non-empty)
- `DATABASE_HOST`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD` (and optional `DATABASE_PORT`)
- `ROSETTA_API_URL`

You will also usually set:

- `ENVIRONMENT_NAME`
- `ALLOWED_HOSTS`
- `WAGTAILADMIN_BASE_URL`, `WAGTAILAPI_BASE_URL`, `WAGTAILAPI_MEDIA_BASE_URL`
- `CSRF_TRUSTED_ORIGINS`

## Operational recommendations

- Use unique `SECRET_KEY` values per environment.
- Keep secrets out of source control.
- Review cache settings (`REDIS_URL`, `CACHE_DEFAULT_TIMEOUT`) when enabling Redis.
- Review telemetry settings (`SENTRY_DSN`, `SENTRY_SAMPLE_RATE`) per environment.
