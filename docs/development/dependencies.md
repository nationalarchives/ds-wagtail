# Dependency management

Managing dependencies can be done using the `dev` container as this comes preinstalled with Poetry.

## Updating to latest builds

e.g. `x.y.1` -> `x.y.2`

```sh
# Update Poetry and NPM dependencies
docker compose exec dev upgrade

# Update Poetry dependencies
docker compose exec dev upgrade poetry

# Update NPM dependencies
docker compose exec dev upgrade npm
```

## Major or minor updates or adding new dependencies

e.g. `x.1.z` -> `x.2.z` or `1.y.z` -> `2.y.z`

```sh
# Update the tna-frontend-jinja package to 0.5.0 in Poetry
docker compose exec dev poetry add tna-frontend-jinja=0.5.0

# Update the tna-frontend package to 0.5.0 in npm
npm i @nationalarchives/frontend@0.5.0

# After installing, rebuild the app container
docker compose up --build -d app
```

See the [Poetry docs](https://python-poetry.org/docs/cli/#add) for more options.

## Removing a dependency

```sh
# Remove the pendulum package
docker compose exec dev poetry remove pendulum

# Remove the jquery package
npm remove jquery

# After removing, rebuild the app container
docker compose up --build -d app
```
