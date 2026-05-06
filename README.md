# TNA Wagtail CMS

## Quickstart

```sh
# Copy the example .env file
cp .env.example .env

# Set .env values for:
#   - ROSETTA_API_URL

# Build and start the containers
docker compose up -d

# Build the Wagtail search index (required when using Elasticsearch)
docker compose exec app poetry run python manage.py update_index
```

View the site on [localhost:8000](http://localhost:8000).

Log in to the Wagtail Admin on [localhost:8000/admin](http://localhost:8000/admin) with the credentials:

- Username: `admin`
- Password: `admin`

## Local Elasticsearch backend

The Docker Compose setup includes an Elasticsearch container for local search indexing.

- Elasticsearch endpoint: http://localhost:9200
- App container endpoint: http://elasticsearch:9200

By default, `.env.example` keeps `WAGTAIL_SEARCH_BACKEND=database`.
To use Elasticsearch locally, set `WAGTAIL_SEARCH_BACKEND=elasticsearch` in your `.env` file.
You can also set `WAGTAILSEARCH_INDEX_PREFIX` if you want a custom index namespace.

## Project documentation

This project contains technical documentation written in Markdown in the `/docs` folder. The latest build from the working branch can be viewed online at [nationalarchives.github.io/ds-wagtail](https://nationalarchives.github.io/ds-wagtail/).

You can also view it locally on http://localhost:8001/ which is served from the `docs` container.
