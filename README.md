# TNA Wagtail CMS

## Quickstart

```sh
# Copy the example .env file
cp .env.example .env

# Set .env values for:
#   - ROSETTA_API_URL

# Build and start the containers
docker compose up -d
```

View the site on [localhost:8000](http://localhost:8000).

Log in to the Wagtail Admin on [localhost:8000/admin](http://localhost:8000/admin) with the credentials:

- Username: `admin`
- Password: `admin`

## Project documentation

This project contains technical documentation written in Markdown in the `/docs` folder. The latest build from the working branch can be viewed online at [nationalarchives.github.io/ds-wagtail](https://nationalarchives.github.io/ds-wagtail/).

You can also view it locally on http://localhost:8001/ which is served from the `docs` container.
