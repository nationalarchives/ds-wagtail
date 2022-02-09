# Etna

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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

#### `cli`

A service with the Platform.sh CLI, PHP and few other packages to help with copying of data and media from the environments running in Platform.sh

## Getting started

NOTE: For any of the following commands to work, you must first [install Fabric](https://www.fabfile.org/installing.html). Once installed, you can type `fab -l` to see a list of available commands.

### 1. Create `.env`

```console
$ cp .env.example .env
```

### 2. Build Docker containers

```console
$ fab build
```

### 3. Start Docker containers

```console
$ fab start
```

### 4. Start a shell session with the 'web' container

```console
$ fab sh
```

### 5. Apply database migrations

```console
$ python manage.py migrate
```

### 6. Run the 'development' web server

```console
$ python manage.py runserver 0.0.0.0:8000
```

### 7. Access the site

<http://127.0.0.1:8000>

**Note: compiled CSS is not included and therefore needs to be built initially, and after each git pull. See the "Working with SASS/CSS section**

### 8. Create a Django user for yourself

```console
$ python manage.py createsuperuser
```

### 9. Access the admin

Navigate to the admin URL in your browser, and sign in using the username/password combination you chose in the previous step.

<http://127.0.0.1:8000/admin/>

## Quick start with `fab run`

While it's handy to be able to access 'web' via a shell and interact with Django directly, sometimes all you want is to view the site in a web browser. In these cases, you can use:

```console
$ fab run
```

This command takes care of the following:

1. Starting all of the necessary Docker containers
2. Installing any new python dependencies
3. Applying any new database migrations
4. Starting the Django development server

You can then access the site in your browser as usual:

<http://127.0.0.1:8000>


## Working with production data locally

### Prerequisites

The following steps must be completed before you can pull data from an evironment:

1. [Register for a Platform.sh account](https://auth.api.platform.sh/register) using your work email.
2. On the `#ds-etna` or `#dev-etna` Slack channels, request for someone to grant you access to the Etna project.
3. Once you have access, [generate an API token](https://docs.platform.sh/development/cli/api-tokens.html#get-a-token) for your account (The name **Local CLI** will do nicely), and add it your local `.env` file as `PLATFORMSH_CLI_TOKEN`.

### Download production data

```console
$ fab pull-production-data
```

**NOTE:** Data is automatically anonymised after downloading to protect sensitive data, so user logins from production will NOT work locally. Also, any Django users you created locally before running the command will no longer exist. You can run `python manage.py createsuperuser` from a container shell to create yourself a new one.

### Download production media

```console
$ fab pull-production-media
```

## Copying content to another development instance

To copy uploaded files, zip up your `/media` directory and replace the second
site's `/media` with the contents of the zip.

To copy your CMS's content, **export** the database:

`docker-compose exec db pg_dump postgres -U postgres --clean > <database-dump>`

And then **import**:

`cat <database-dump> |  docker-compose exec  -T db psql -U postgres postgres`

## Generating database migrations

To run any Django management command, first access the shell using:

```console
$ fab sh
```

To make migrations for a new app:

```console
$ python manage.py makemigrations [appname]
```

To make migrations for an existing app, use the `-n` argument to provide a meaninful name to help your peers understand what the migration does:

```console
$ python manage.py makemigrations [appname] -n meaningful_name_here
```

## Front end development

### Working with SASS/CSS

- Ensure you have NodeJS & NPM installed.
- Install SASS globally by running `npm install -g sass`.
- To watch and build the public facing site SASS, run `sass --watch sass/etna.scss:templates/static/css/dist/etna.css`
- To watch and build the Wagtail editor SASS, run `sass --watch sass/etna-wagtail-editor.scss:templates/static/css/dist/etna-wagtail-editor.css`
- To modify styles, navigate to the `sass` folder in your editor.

### Working with JavaScript

Webpack is used for JavaScript module bundling with entry points and outputs defined within `webpack.config.js`. When defining new
entry points remember to avoid, where possible, sending JavaScript to a given page where it is not required.

- Install dependencies with `npm install`
    - _For development_: Kick off a Webpack watch task with `npm start`. This will produce development assets (by overriding the production mode set in `webpack.config.js`).
    - _For production_: bundle assets with `npx webpack --config webpack.config.js`

#### JavaScript testing

Jest is used for JavaScript testing. Tests should be added as siblings of the target file and given the same name with a `.test.js` suffix. Let's aim for 100% coverage. Where necessary Jest can be set to run in a browser-like environment by setting the Jest environment to `jsdom` via a docblock at the top of the file.

- Run Jest unit tests with `npm test`

## Kong

To fetch data from the Kong API during development, a valid API key
needs to be added to `.env` (`KONG_CLIENT_KEY`). This will allow your container
to fetch the external data required to render explorer result and details
pages.

## Categories

The icons used by the categories snippets can be selected from a list of the svg files in the path `static/images/category-svgs/` under the categories app itself.

The reason for this is to protect from potential 500 errors should a file be deleted or renamed.

If additional category icons are required, they should be added to the directory above. Once added, icons should not be renamed or removed unless it is **absolutely certain** they are not in use by any category snippet.
