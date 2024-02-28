# Dependency management

Using the dev container (`fab dev`) should give you access to commands such as `update-poetry` and `update-npm` which should update the `package.json`, `package-lock.json`, `pyproject.toml` and/or `poetry.lock` files ready to commit to version control.

## Updating build numbers

e.g. `x.y.1` -> `x.y.2`

1. Run `fab dev`
1. Run `update-poetry` (Python) or `update-npm` (npm)

## Major or minor numbers

e.g. `x.1.z` -> `x.2.z` or `1.y.z` -> `2.y.z`

1. Update version numbers in `pyproject.toml` (Python) or `package.json` (npm)
1. Run `fab dev`
1. Run `update-poetry` (Python) or `update-npm` (npm)

## Adding a dependency

Use the following to automatically use the latest version (e.g. [pendulum](https://pypi.org/project/pendulum/)):

```sh
fab dev
poetry add pendulum
update-poetry
```

Or, specify a version:

```sh
fab dev
poetry add pendulum@^2.1.2
poetry add "pendulum@>=2.1.2"
update-poetry
```

See the [Poetry docs](https://python-poetry.org/docs/cli/#add) for more options.

### Removing a dependency

```sh
fab dev
poetry remove pendulum
update-poetry
```
