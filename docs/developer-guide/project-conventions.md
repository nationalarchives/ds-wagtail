# Etna project conventions

At TNA we follow a set of conventions for our projects to ensure consistency and quality across our codebases. These can be found in our [developer handbook](https://nationalarchives.github.io/developer-handbook/) and should be followed when contributing to the Etna project, as well as the guidance below.

## Docker for local development

Etna uses Docker to create a consistent environment for local development.
For more information on Docker inside our project see the [Docker guide](docker.md).

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
official [python 3.11](https://hub.docker.com/_/python/) base image

During the build step our custom container installs our project's dependencies
using [Poetry](https://python-poetry.org) as defined in `pypproject.toml` using the approprpriate versions outlined in `Poetry.lock`

Build steps for the `web` container are defined in the project's `Dockerfile`.

Our `web` container has a [dependency](https://docs.docker.com/compose/compose-file/compose-file-v3/#depends_on) on the `db` container, as Django/Wagtail will not run without a database to connect to.

### `dev`

This container is used to run development commands on the `web` container, such as `manage.py` commands and `poetry` commands.

Build steps for the `dev` container are defined in the project's `dev/Dockerfile`.

### `cli`

A service with the Platform.sh CLI, PHP and few other packages to help with copying of data and media from the environments running in Platform.sh.

## Code style and standards

### Python

The Etna project uses a few tools to improve the consistency and quality of Python code:

- [``Black``](https://black.readthedocs.io/en/stable/): An opinionated Python formatter that takes care of code formatting (so we don't have to think about it).
- [``isort``](https://pycqa.github.io/isort/): Ensures that import statements are ordered in a consistant way accross the project.
- [``flake8``](https://flake8.pycqa.org/en/stable/): Catches things like unused parameters, unused imports and other non-formatting related things.

The easiest way to ensure the code you're contributing adheres to these standards is to find and install plugins for your code editor of choice, that will check and transparently reformat your code whenever you save changes. Standard configuration files are included in the root of the repository, which *should* be picked up and respected by such plugins.

Another option is to run the `format` Fabric command from your console to apply `isort` and `Black` formatting to Python code:

```console
$ fab format
```

`flake8` will just flag things in the terminal, it will not update any code for you like `isort` or `Black`.

Compliance checks are also built in to the `test` Fabric command - you just need to use the ``--lint`` option to activate them. For example:

```console
$ fab test --lint
```

This will be checked by CI on every commit, so it's a good idea to run this locally before pushing your changes.

We also have CI to check Django migrations, in order to help prevent any potential data issues. The CI will only run on a pull request, if any `/migrations` folders have been changed.

While this won't entirely stop potential data issues, it will help to catch any potential issues by forcing the developer to check that their migrations are sound, before they
are deployed.

### SASS/CSS and Javascript

The Etna project uses a few tools to improve the consistency and quality of SASS/CSS and JavaScript code:

- [``Prettier``](https://prettier.io/): An opinionated front-end code formatter that takes care of code formatting (so we don't have to think about it).

To run `Prettier` against your code, simply run the `format` Fabric command from your console:

```console
$ fab format
```

This will be checked by CI on every commit, so it's a good idea to run this locally before pushing your changes.

## Git/Github conventions

### Branching model

We follow a loose version of the [Git flow branching model](https://nvie.com/posts/a-successful-git-branching-model/).

- Changes are developed in feature branches and submitted as pull requests via Github
- Feature branches should always be based on: `develop`
- Release branches should always be based on: `develop`
- Release branches should be merged via PR into `main`, followed by PR to merge `main` into `develop`

**See below for merging guidance**

### Naming branches

- Use only alphanumeric characters and hyphens where possible and avoid special characters.
- Branch names for ticketed new features should follow: `feature/JIRA-TICKET-NUMBER-with-short-description`
- Branch names for ticketed bug fixes should follow: `fix/JIRA-TICKET-NUMBER-with-short-description`
- Branch names for releases should follow: `release/major.minor.patch`
- Branch names for housekeeping tasks or other unticketed work should follow: `chore/short-description`
- For example:
    - `feature/UN-123-extra-squiggles`
    - `fix/DF-999-image-view-error`
    - `release/1.0.0`
    - `chore/update-documentation`

### Naming pull requests

- Pull requests for features and bug fixes should be titled: `JIRA-TICKET-NUMBER: short-description`
- Pull requests for release branches should be titled: `Release X.X.X into main`
- Pull requests for housekeeping tasks or other unticketed work should be titled: `CHORE: short-description`
- For example:
    - `UN-123: Add extra squiggles`
    - `DF-999: Fix image view error`
    - `Release 1.0.0 into main`
    - `CHORE: Update documentation`

### Merging branches

**NOTE:** Where possible, a feature branch should be kept up-to-date with `develop` by regularly merging `develop` into the feature branch. This will help to prevent conflicts when merging the feature branch back into `develop`, and ensure there are no inconsistencies.

- When merging a feature branch into `develop`, use the `Squash and merge` option to keep the commit history clean
- When merging a release branch into `main`, use the `Merge commit` option to keep the commit history continuous from `develop`
- When merging `main` back into `develop` (after merging a release branch into `main`), use the `Merge commit` option to prevent any conflicts when merging future releases into `main` to keep the history in sync
    - This should be named `Release X.X.X main into develop` to make it clear what the merge is for