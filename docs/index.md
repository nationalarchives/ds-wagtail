# Welcome

⚠️ IMPORTANT: Remember that this documentation is public. Treat any sensitive data or credentials with the same level of caution that you would on any public forum.

## Quickstart

To create all the relevant Docker containers, run:

```sh
# Build and start the containers defined in docker-compose.yml
docker compose up -d
```

To get data and media from the host platform, check out [fetching data](./development/fetching-data.md).

## Run tests

To run the test suite, use the following command:

```sh
docker compose exec app poetry run pytest --ds=config.settings.test
```

To refresh API response snapshots after an intentional API response change, use the following command:

```sh
docker compose exec -e UPDATE_API_EXPECTED_RESULTS=1 app poetry run pytest --ds=config.settings.test app/api/tests/test_pages.py
```

## Updating this documentation

The navigation for this documentation is configured in `mkdocs.yml`. You can add new markdown files there to get them to appear in the navigation.

You can preview changes locally by starting the `docs` container (if it isn't already running):

```sh
docker compose up -d docs
```

This will make your local copy of the documentation available in your browser at:
http://localhost:8001/
