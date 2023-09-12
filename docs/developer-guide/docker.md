# Working with Docker

The `Dockerfile` is used to create containers for both local development and deployment to AWS and performs the following steps:

1. Defines the exposed port (`8000`)
1. Declares environment variables needed to run Python and install Poetry in a consistent manner
1. Creates a [non-root user](#non-root-user) (`app`) with a home directory (`/home/app`)
1. Creates a directory `/app` to store the application code in which can be written to only by `root` and the new `app` users and is owned by `app`
1. Sets the working directory to `/app`
1. Sets the active user to `app`
1. Sets a [pipefail](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#using-pipes) to ensure one failed command in a piped statment breaks the pipe
1. Installs Poetry in the `app` user's home directory (`/home/app`)
1. Copies in the dependency requirement files (`pyproject.toml` and `poetry.lock`)
1. Installs the project dependencies with Poetry
1. Copies in all the application code
1. Ensures the run script can be executed by the current user
1. Copies in the compiled static assets (CSS and JavaScript)
1. Collects the static assets for the project
1. Starts the service by running `/app/bash/run.sh`

## Multistage build

To compile the CSS and JavaScript with the intention of not poulting the Python image with npm (which could increase the number of attack vectors and potentially create a larger and slower image) the assets are compiled separately and copied in with `--from=staticassets`.

The first image in the `Dockerfile` (aliased as `staticassets`) is a Node image which uses only the minimum files to build everything.

This compilation can be run in parallel with the main Docker build for increaed speed and better caching.

## Local development

Locally, the containers can be created with `fab build` which sits atop `docker-compose`. `fab build && fab start` is an alias to:

```sh
# Build and start the containers defined in docker-compose.yml
docker-compose up -d
```

### Volumes

The volumes menioted in the `docker-compose.yml` are:

```yml
volumes:
  - ./:/app
  - ~/.nvm:/home/app/.nvm
```

The first volume is the project directory which is copied into the `/app` directory of the container. This is the same directory as the "final" Docker image and allows us the ability to watch and rebuild our application whilst developing.

The second is an alias to [NVM](https://github.com/nvm-sh/nvm) which is used to ensure that the assets compilation is always done by the same version of Node. If you have NVM installed locally then this saves us downloading and installing NVM inside the container, saving time when starting up the container.

### Run command

The standard `/app/bash/run.sh` script defined in the `Dockerfile` is overwritten locally by a development-specific run script:

```yml
command: sh /app/bash/run-dev.sh
```

Instead of running migrations and then starting up `gunicorn` with production-level values, this script will:

1. Install NVM inside the container (if it doesn't already exist)
1. Start watching the local SCSS and JavaScript files and rebuild them when they change
1. Run migrations and start the development server (if `AUTO_START_SERVER=true` has been added to your `.env` file)

If `AUTO_START_SERVER` is omitted or falsy then the container will sit and await commands and can be accessed with the normal `fab sh` command.

## Non-root user

During the creation of the Docker image, we create a non-root user, `app`.

By creating this user and running all commands as them, the chance that someone would be able to find and exploit a way to execute commands as the root user is greatly reduced.
