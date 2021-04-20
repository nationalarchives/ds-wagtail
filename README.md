# Etna

## Local development

### Docker

Etna uses Docker to create a consistent environment for local development.

On macOS and Windows, Docker requires [Docker
Desktop](https://www.docker.com/products/docker-desktop) to be installed. Linux
users should install the Docker engine using their distribution's package
manager or [download a `.deb` or
`.rpm`](https://docs.docker.com/engine/install/)

Once installed, we need to build our containers. We use
[`docker-compose`](https://docs.docker.com/compose/) to orchestrate the
building of the project's containers, one for each each service:

#### `db`

The database service built from the official [postgres](https://hub.docker.com/_/postgres/) image

#### `elasticsearch`

The search backend, build from the official [elasticsearch](https://hub.docker.com/_/elasticsearch/) image

#### `web`

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

### Getting started

#### Create `.env`

`cp .env.example .env`

#### Docker

##### Build containers

`docker-compose build`

##### Run containers (in background)

`docker-compose up --detach`

#### Database

##### Run migrations

`docker-compose exec web poetry run python manage.py migrate`

#### User management

`docker-compose exec web poetry run python manage.py createsuperuser --username sysadmin`

##### Access site

<http://127.0.0.1:8000>

*Note: compiled CSS is not included and therefore needs to be built initially, and after each git pull. See the "Working with SASS/CSS section*

##### Access site admin

Log in using `sysadmin`, along with the password set with `createsuperuser` command.

<http://127.0.0.1:8000/admin/>

##### Working with SASS/CSS

- Ensure you have NodeJS & NPM installed.
- Install SASS globally by running `npm install -g sass`.
- To watch and build the SASS, run `sass --watch sass/etna.scss:static/css/dist/etna.css`
- To modify styles, navigate to the `sass` folder in your editor.