# Backend development

Specific guidance for working on on backend tasks.

## Running Django management commands

Locally, Django runs in the `web` container, and its commands are invoked via the shell.

The `web` container runs as a non-root user so performing actions such as making migrations must be done in the `dev` container that does run as a root user.

To start a shell session with your local `dev` container, run:

```sh
fab dev
```

From there, you can interact with Django exactly as you can see outlined in [the official documentation](https://docs.djangoproject.com/en/stable/topics/migrations/#module-django.db.migrations) and the many tutorials you'll find on the web.

There is a command `manage ...` that aliases `poetry run python /app/manage.py ...` to make running commands easier.

## Common Django management commands

Below are some commands you'll use regularly:

### Generating database migrations

To make migrations for a new app:

```sh
manage makemigrations [appname]
```

To make migrations for an existing app, use the `-n` argument to provide a meaninful name to help your peers understand what the migration does:

```sh
manage makemigrations [appname] -n meaningful_name_here
```

### Applying database migrations

To apply migrations for all apps:

```sh
manage migrate
```

To apply migrations for a specific app:

```sh
manage migrate appname
```

### Reversing database migrations

To reverse migrations for an app, specify the number of the migration you want to **revert back to**. For example, if you wanted to reverse the following migrations:

- `003_add_cat_gif_image_field`
- `004_tweak_streamfield_options`
- `005_add_fks_to_insights_pages`

You would run:

```sh
manage migrate appname 002
```

If you need to reverse ALL migrations for an app, use the 'zero' keyword, like so:

```sh
manage migrate appname zero
```
