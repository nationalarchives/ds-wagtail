# Environment variables

This project reads environment variables at runtime from the Django settings modules in `config/settings`. Most values are loaded with `os.getenv(...)` and used to configure the database, caches, logging, email, Wagtail URLs, and feature flags.

How the values are set depends on the environment:

- For local development, values are provided by `docker-compose.yml` and by the local `.env` file copied from `.env.example`.
- For deployed environments, values are managed in the infrastructure configuration used by `ds-infrastructure-web`.
- Some settings have defaults in the Django settings files, so the app can still start even if a value is not set explicitly.

## How the project uses env vars

The settings modules use environment variables to control behaviour without changing code. Common examples include:

- `DATABASE_*` for the database connection
- `REDIS_URL` and `CACHE_DEFAULT_TIMEOUT` for caching
- `SENTRY_DSN` and `SENTRY_SAMPLE_RATE` for error reporting
- `WAGTAILADMIN_BASE_URL`, `WAGTAILAPI_BASE_URL`, and `WAGTAILAPI_MEDIA_BASE_URL` for generated URLs
- `EMAIL_*` for outbound mail
- `DEBUG`, `LOG_LEVEL`, and `WAGTAIL_2FA_REQUIRED` for runtime behaviour

If a variable is required and missing, the settings code may raise an error. For example, `SECRET_KEY` must be set before Django can start.

## How to set env vars

### Local development

Copy `.env.example` to `.env`, then set any local overrides you need. The container definitions in `docker-compose.yml` also provide values directly, which is why the application can usually run with minimal local setup.

### Deployed environments

Environment-specific values are managed outside this repository in `ds-infrastructure-web`. That is where the platform team updates the configuration for each environment.

### Defaults in code

Some variables have defaults in the settings modules. These defaults are used only when no environment value has been provided.

## Table of environment variables

The canonical table of environment variables is maintained in the [README environment variables section](https://github.com/nationalarchives/ds-wagtail?tab=readme-ov-file#environment-variables) to avoid duplication.
