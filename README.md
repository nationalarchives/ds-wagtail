# Etna

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Project documentation

This project contains technical documentation written in Markdown in the /docs folder. The latest build (from the `develop` branch) can be viewed online at:
https://nationalarchives.github.io/ds-wagtail/

You can also view it locally on http://localhost:8001/ which is booted as the `docs` container.

## Setting up a local build

Local development is done in Docker. You can [find out more about this here](https://nationalarchives.github.io/ds-wagtail/developer-guide/project-conventions/).

Convenience commands have been added to `fabfile.py` to help you interact with the various services. But, for any of these commands to work, you must first [install Fabric](https://www.fabfile.org/installing.html).

Once installed, you can type `fab -l` to see a list of available commands.

### Before starting a build for the first time

```sh
cp .env.example .env
```

Populate values for:

- `KONG_CLIENT_BASE_URL`
- `KONG_IMAGE_PREVIEW_BASE_URL`
- `KONG_CLIENT_KEY`
- `PLATFORMSH_CLI_TOKEN`

### 1. Build and start Docker containers

```sh
docker compose up -d
```

### 2. Access the site

<http://127.0.0.1:8000>

### 3. Access the Wagtail admin

Navigate to the admin URL in your browser, and sign in using the username/password combination you chose in the previous step.

<http://127.0.0.1:8000/admin/>

## Issues with your local environment?

Check out the [Local development gotchas](https://nationalarchives.github.io/ds-wagtail/developer-guide/local-development-gotchas/) page for solutions to common issues.

## Discover more

- [Documentation home](https://nationalarchives.github.io/ds-wagtail/)
- [Project conventions](https://nationalarchives.github.io/ds-wagtail/developer-guide/project-conventions/)
- [Backend development guide](https://nationalarchives.github.io/ds-wagtail/developer-guide/backend/)
- [Frontend development guide](https://nationalarchives.github.io/ds-wagtail/developer-guide/frontend/)
- [Fetching data](https://nationalarchives.github.io/ds-wagtail/developer-guide/fetching-data/)
