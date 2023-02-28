# Etna project conventions

## Docker for local development

Etna uses Docker to create a consistent environment for local development.

On macOS and Windows, Docker requires [Docker
Desktop](https://www.docker.com/products/docker-desktop) to be installed. Linux
users should install the Docker engine using their distribution's package
manager or [download a `.deb` or
`.rpm`](https://docs.docker.com/engine/install/)

Once installed, we need to build our containers. We use
[`docker-compose`](https://docs.docker.com/compose/) to orchestrate the
building of the project's containers, one for each each service:

### `db`

The database service built from the official [postgres](https://hub.docker.com/_/postgres/) image

### `web`

Our custom container responsible for running the application. Built from the
official [python 3.10](https://hub.docker.com/_/python/) base image

During the build step our custom container installs our project's dependencies
using [Poetry](https://python-poetry.org) as defined in
[`pypproject.toml`](pyproject.toml) using the approprpriate versions outlined
in [`Poetry.lock`](Poetry.lock)

Build steps for the `web` container are defined in the project's [`Dockerfile`](Dockerfile).

Our `web` container
[depends](https://docs.docker.com/compose/compose-file/compose-file-v3/#depends_on)
has a dependency on the `db` container, as Django/Wagtail will not run without a database to connect to.

### `cli`

A service with the Platform.sh CLI, PHP and few other packages to help with copying of data and media from the environments running in Platform.sh

## Code style and standards

### For Python

The Etna project uses a few tools to improve the consistency and quality of Python code:

- [``Black``](https://black.readthedocs.io/en/stable/): An opinionated Python formatter that takes care of code formatting (so we don't have to think about it).
- [``isort``](https://pycqa.github.io/isort/): Ensures that import statements are ordered in a consistant way accross the project.
- [``flake8``](https://flake8.pycqa.org/en/stable/): Catches things like unused parameters, unused imports and other non-formatting related things.

The easiest way to ensure the code you're contributing adheres to these standards is to find and install plugins for your code editor of choice, that will check and transparently reformat your code whenever you save changes. Standard configuration files are included in the root of the repository, which *should* be picked up and respected by such plugins.

Another option is to run the `format` Fabric command from your console to apply `isort` and `Black` formatting to Python code:

```console
$ fab format
```

Compliance checks are also built in to the `test` Fabric command - you just need to use the ``--lint`` option to activate them. For example:

```console
$ fab test --lint
```

### For SASS/CSS

TBC

### For Javascript

TBC

## Git branching model

We follow a loose version of the [Git flow branching model](https://nvie.com/posts/a-successful-git-branching-model/).

- Changes are developed in feature branches and submitted as pull requests via Github
- Feature branches should always be based on: `develop`
- Release branches should always be based on: `develop`
- Release branches should be merged via PR into `main`, followed by PR to merge `main` into `develop`.

### Naming branches

- Branch names for ticketed new features should start with: `feature/<JIRA-TICKET-with-short-description>`.
- Branch names for ticketed bugs should start with: `fix/<JIRA-TICKET-with-short-description>`.
- Branch names for release should start with: `release/<major.minor.patch>`.
- Branch names for housekeeping tasks or other unticketed work should start with: `chore/<short-description>`
- Ticket numbers should be included in branch names wherever possible. For example:
  - `feature/DF-123-extra-squiggles`
  - `fix/DF-999-image-view-error`
  - `chore/short-description`
- Stick with alphanumeric characters and hyphens where possible and avoid random special characters.
