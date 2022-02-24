# Etna project conventions

[TOC]

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

### `elasticsearch`

The search backend, build from the official [elasticsearch](https://hub.docker.com/_/elasticsearch/) image

### `web`

Our custom container responsible for running the application. Built from the
official [python 3.9](https://hub.docker.com/_/python/) base image

During the build step our custom container installs our project's dependencies
using [Poetry](https://python-poetry.org) as defined in
[`pypproject.toml`](pyproject.toml) using the approprpriate versions outlined
in [`Poetry.lock`](Poetry.lock)

Build steps for the `web` container are defined in the project's [`Dockerfile`](Dockerfile).

Our `web` container
[depends](https://docs.docker.com/compose/compose-file/compose-file-v3/#depends_on)
on both the `db` and `elasticsearch` containers in order for the `web`
container to communicate with those services.

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
- Feature branches should always be based on: `main`
- Pull requests should always be merged to: `main`

### Naming feature branches

- Branch names for new features should start with: `feature/`.
- Branch names for ticketed bugs should start with: `fix/`.
- Branch names for housekeeping tasks or other unticketed work should start with: `chore/`
- Ticket numbers should be included in branch names wherever possible. For example:
    - `feature/df123-extra-squiggles`
    - `fix/df999-image-view-error`
- Stick with alphanumeric characters and hyphens where possible and avoid random special characters.

## Contributing to the codebase

General advice:

- Submit pull-requests sooner rather than later: CI feedback is your friend, not your enemy
- Mark in-progress PRs as drafts until they are ready for review.
- Don't be afraid to show your working. We're all learning. If you need help, linking to code changes in a PR is a quick and easy way to explain the problem.

### Submitting a pull request (PR)

1. Push your branch to the remote.
2. Head to https://github.com/nationalarchives/ds-wagtail/pulls and create a pull request from your branch.
    - For ticketed features of bug fixes, use the naming convention: `DF-XXX: Ticket name`.
    - For other fixes use the convention: `Fix: Short description`.
    - For housekeeping tasks or other unticketed work, use the convention: `Chore: Short description`.
3. To mark a PR as a draft, look for the **"Convert to draft"** link (after submitting) and click on it.
4. When you are finished (and CI is passing): Add a useful description, mark the PR as "Ready to review", and request a review from another developer.
