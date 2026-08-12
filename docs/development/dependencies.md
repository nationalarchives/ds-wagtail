# Dependency management

Managing dependencies can be done using the `app` container as this has Poetry installed.

## Automated updates

This project uses [Renovate](https://docs.renovatebot.com/) to automatically update packages and flag any updates/vulnerabilities in our existing packages. The config can be seen in [`renovate.json`](https://github.com/nationalarchives/ds-wagtail/blob/main/.github/renovate.json) However, manual intervention is sometimes required.

## Updating to latest versions

Renovate strongly suggests that pinned package versions in `pyproject.toml` are the explicit version, rather than careted `^x.y.z` or tilded `~x.y`. This means that to update any versions, you must first update the pinned version in `pyproject.toml` to the required version, e.g. `wagtail = "7.4.2" -> wagtail = "7.5.0"`.

After that, you can run:

```sh
docker compose exec app poetry update
```

to update the `poetry.lock` with the latest version(s).

## Adding new dependencies

```sh
# Add the tna-frontend-jinja package with version 0.5.0 in Poetry
docker compose exec app poetry add tna-frontend-jinja=0.5.0
```

See the [Poetry docs](https://python-poetry.org/docs/cli/#add) for more options.

## Removing a dependency

```sh
# Remove the pendulum package
docker compose exec app poetry remove tna-frontend-jinja
```

## Dependency compatibility

Please ensure that dependencies are:

- Checked for any vulnerabilities
- At least 7 days old before adoption (see `min-release-age = 7` in `pyproject.toml`)
- Compatible with our pinned core stack versions (notably Python, Django, and Wagtail)
- Not yanked and not pre-release, unless there is a clear, agreed reason
- Actively maintained (recent releases, issue activity, and clear project ownership)
- Acceptable from a licensing and compliance perspective
- Reviewed for breaking changes in release notes/changelog
- Security-sensitive dependencies should get extra scrutiny

Before merging dependency changes, run tests and checks locally:

```sh
docker compose exec app poetry run pytest
docker compose exec app poetry run python manage.py check
```
