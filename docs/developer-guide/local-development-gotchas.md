# Local development gotchas

This page lists common local development issues and how do resolve them.

## How do I disable Django's 'Debug mode' locally?

Sometimes you need to disable Django's DEBUG mode in order to test certain behaviours. To do this, you have two options:

1. Add `DEBUG = False` to `config/settings/local.py`
2. Add `DEBUG=False` to your `.env` file

### Making static files work

Guidance from Django Documentation: https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#cmdoption-runserver-insecure

Add in `config/settings/local.py`
```console
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
```

Run the `development` web server

```console
python manage.py runserver 0.0.0.0:8000 --insecure
```

## How do I disable Django Debug Toolbar?

If you don't need Django's debugging tools, setting `DEBUG=False` as detailed above will disable Django Debug Toolbar also.

If you still need Django's debugging tools, but don't want to use Django Debug Toolbar for any reason, you have two options for disabling it:

1. Add `DEBUG_TOOLBAR_ENABLED = False` to `config/settings/local.py` 
2. Add `DEBUG_TOOLBAR_ENABLED=False` to your `.env` file

## I see an error when viewing the 'Explore the Collection' page on my local build

Ensure you have the relevant entries for the `KONG_*` settings in your `.env` file - ask another developer to supply the correct keys if necessary.
