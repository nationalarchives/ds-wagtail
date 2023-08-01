# Dependency management

## Updating all dependencies

From the host machine, run:

```sh
fab update-deps
```

This will start two Docker machines, one to update npm and the other to update Poetry.

The `package.json`, `package-lock.json`, `pyproject.toml` and `poetry.lock` files should then be updated and ready to commit.

## For the backend

The Etna project uses [Poetry](https://python-poetry.org/docs/) to manage Python dependencies, which uses lock-file to help ensure environment consistency.

Locally, Poetry runs in the `web` container, and it's commands are invoked via the shell. To start a shell session with your local `web` container, run:

```console
$ fab sh
```

You can then run Poetry commands exactly [as they are documented here](https://python-poetry.org/docs/cli/).

### Updating local dependencies to reflect changes

```console
poetry install --remove-untracked --no-root
```

### Adding a dependency

Use the following to automatically use the latest version:

```console
poetry add name-of-dependency
```

Or, specify a version:

```console
poetry add name-of-dependency@^2.0.5
poetry add "name-of-dependency@>=2.0.5"
```

See [the Poetry docs](https://python-poetry.org/docs/cli/#add) for more options.

### Removing a dependency

```console
poetry remove name-of-dependency
```

## For the frontend

TBC
