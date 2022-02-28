# Backend development

Specific guidance for working on on backend tasks.

## Managing Python dependencies

The Etna project uses [Poetry](https://python-poetry.org/docs/) to manage Python dependencies, which uses lock-file to help ensure environment consistency.

Locally, Poetry runs in the `web` container, and it's commands are invoked via the shell. To start a shell session with your local `web` container, run:

```console
$ fab sh
```

You can then run Poetry commands exactly [as they are documented here](https://python-poetry.org/docs/cli/).

Here are the ones you'll use regularly:

### Updating local dependencies to reflect changes

```console
poetry install --remove-untracked --no-root"
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

## Running Django management commands

Locally, Django runs in the `web` container, and it's commands are invoked via the shell. To start a shell session with your local `web` container, run:

```console
$ fab sh
```

From there, you can interact with Django exactly as you can see outlined in [the official documentation](https://docs.djangoproject.com/en/stable/topics/migrations/#module-django.db.migrations) and the many tutorials you'll find on the web.

## Common Django management commands

Below are some commands you'll use regularly:

### Generating database migrations

To make migrations for a new app:

```console
$ python manage.py makemigrations [appname]
```

To make migrations for an existing app, use the `-n` argument to provide a meaninful name to help your peers understand what the migration does:

```console
$ python manage.py makemigrations [appname] -n meaningful_name_here
```

### Applying database migrations

To apply migrations for all apps:

```console
$ python manage.py migrate
```

To apply migrations for a specific app:

```console
$ python manage.py migrate appname
```

### Reversing database migrations

To reverse migrations for an app, specify the number of the migration you want to **revert back to**. For example, if you wanted to reverse the following migrations:

- `003_add_cat_gif_image_field`
- `004_tweak_streamfield_options`
- `005_add_fks_to_insights_pages`

You would run:

```console
$ python manage.py migrate appname 002
```

If you need to reverse ALL migrations for an app, use the 'zero' keyword, like so:

```console
$ python manage.py migrate appname zero
```
