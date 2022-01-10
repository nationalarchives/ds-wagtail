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

NOTE: For any of the following commands to work, you must first [install Fabric](https://www.fabfile.org/installing.html). Once installed, you can type `fab -l` to see a list of available commands.

#### Create `.env`

```console
$ cp .env.example .env
```

#### Build Docker containers

```console
$ fab build
```

#### Run Docker containers

```console
$ fab start
```

#### Access a container shell

```console
$ fab sh
```

#### Run database migrations

```console
$ python manage.py migrate
```

#### Access the site

<http://127.0.0.1:8000>

**Note: compiled CSS is not included and therefore needs to be built initially, and after each git pull. See the "Working with SASS/CSS section**

#### Access the admin site

From a container shell, first create a Django user for yourself using:

```console
$ python manage.py createsuperuser
```

Now, navigate to the admin URL in your browser, and sign in using the username/password combination you chose for your user:

<http://127.0.0.1:8000/admin/>

### Working with production data locally

#### Prerequisites

The following steps must be completed before you can pull data from an evironment:

1. Ask on the `#ds-etna` or `#dev-etna` channels to be granted access to Platform.sh.
2. Once you have access, [follow these instructions](https://docs.platform.sh/development/ssh.html#authenticate-with-ssh-keys) to add your SSH key to your Platform account.
3. Install the Platform.sh CLI, authenticate, and try out some of the commands, by [following these instructions](https://docs.platform.sh/development/cli.html). **For Windows users**: The CLI requires PHP to run. If you haven't done so already, you may also need to [install PHP](https://www.sitepoint.com/how-to-install-php-on-windows/#installphp) before the CLI will work.

#### Download production data

`fab pull-production-data`

**NOTE:** Data is automatically anonymised after downloading to protect sensitive data, so user logins from production will NOT work locally. Also, any Django users you created locally before running the command will no longer exist. You can run `python manage.py createsuperuser` from a container shell to create yourself a new one.

#### Download all production media

`fab pull-production-media`

#### Download production images only

`fab pull-production-images`

### Copying content to another development instance

To copy uploaded files, zip up your `/media` directory and replace the second
site's `/media` with the contents of the zip.

To copy your CMS's content, **export** the database:

`docker-compose exec db pg_dump postgres -U postgres --clean > <database-dump>`

And then **import**:

`cat <database-dump> |  docker-compose exec  -T db psql -U postgres postgres`

### Generating database migrations

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

### Front end development

#### Working with SASS/CSS

- Ensure you have NodeJS & NPM installed.
- Install SASS globally by running `npm install -g sass`.
- To watch and build the public facing site SASS, run `sass --watch sass/etna.scss:templates/static/css/dist/etna.css`
- To watch and build the Wagtail editor SASS, run `sass --watch sass/etna-wagtail-editor.scss:templates/static/css/dist/etna-wagtail-editor.css`
- To modify styles, navigate to the `sass` folder in your editor.

#### Working with JavaScript

Webpack is used for JavaScript module bundling with entry points and outputs defined within `webpack.config.js`. When defining new
entry points remember to avoid, where possible, sending JavaScript to a given page where it is not required.

- Install dependencies with `npm install`
    - _For development_: Kick off a Webpack watch task with `npm start`. This will produce development assets (by overriding the production mode set in `webpack.config.js`).
    - _For production_: bundle assets with `npx webpack --config webpack.config.js`

##### JavaScript testing

Jest is used for JavaScript testing. Tests should be added as siblings of the target file and given the same name with a `.test.js` suffix. Let's aim for 100% coverage. Where necessary Jest can be set to run in a browser-like environment by setting the Jest environment to `jsdom` via a docblock at the top of the file.

- Run Jest unit tests with `npm test`

### Kong

To fetch data from the Kong API during development, a valid API key
needs to be added to `.env` (`KONG_CLIENT_KEY`). This will allow your container
to fetch the external data required to render explorer result and details
pages.

### Categories

The icons used by the categories snippets can be selected from a list of the svg files in the path `static/images/category-svgs/` under the categories app itself.

The reason for this is to protect from potential 500 errors should a file be deleted or renamed.

If additional category icons are required, they should be added to the directory above. Once added, icons should not be renamed or removed unless it is **absolutely certain** they are not in use by any category snippet.
