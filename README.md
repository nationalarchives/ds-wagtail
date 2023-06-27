# Etna

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Project documentation

This project contains technical documentation written in Markdown in the /docs folder. The latest build (from the `develop` branch) can be viewed online at:
https://nationalarchives.github.io/ds-wagtail/


You can also view it locally via [mkdocs](https://www.mkdocs.org/) by running the following from a `web` container shell:

```console
$ mkdocs serve
```

The documentation will be available at:

http://localhost:8001/

## Setting up a local build

Local development is done in Docker. You can [find out more about this here](https://nationalarchives.github.io/ds-wagtail/developer-guide/project-conventions/).

Convenience commands have been added to `fabfile.py` to help you interact with the various services. But, for any of these commands to work, you must first [install Fabric](https://www.fabfile.org/installing.html).

Once installed, you can type `fab -l` to see a list of available commands.


### 1. Build Docker containers

```console
$ fab build
```

### 2. Start Docker containers

```console
$ fab start
```

### 3. Start a shell session with the 'web' container

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

### 9. Access the Wagtail admin

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

## Linux / OSX
If you are running a Unix based operating system, these alias commands may be useful to you to run inside the Docker container.

Running the development server:

``` console
$ djrun
```
Run migrations:

```console
$ dj migrate
```
Create a super user:

```console
$ dj createsuperuser
```

## Issues with your local environment?

Check out the [Local development gotchas](https://nationalarchives.github.io/ds-wagtail/developer-guide/local-development-gotchas/) page for solutions to common issues.

## Discover more

- [Documentation home](https://nationalarchives.github.io/ds-wagtail/)
- [Project conventions](https://nationalarchives.github.io/ds-wagtail/developer-guide/project-conventions/)
- [Backend development guide](https://nationalarchives.github.io/ds-wagtail/developer-guide/backend/)
- [Frontend development guide](https://nationalarchives.github.io/ds-wagtail/developer-guide/frontend/)
- [Fetching data](https://nationalarchives.github.io/ds-wagtail/developer-guide/fetching-data/)
