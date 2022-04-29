## How do I disable Django's 'debug' mode?

Sometimes you need to disable Django's DEBUG mode in order to test certain behaviours. To do this, you have two options:

1. Add `DEBUG = False` to `conf/settings/local.py` 
2. Add `DEBUG=False` to your `.env` file

## How do I disable Django Debug Toolbar?

If you don't need Django's debugging tools, setting `DEBUG=False` as detailed above will disable Django Debug Toolbar also.

If you still need Django's debugging tools, but don't want to use Django Debug Toolbar for any reason, you have two options for disabling it:

1. Add `DEBUG_TOOLBAR_ENABLED = False` to `conf/settings/local.py` 
2. Add `DEBUG_TOOLBAR_ENABLED=False` to your `.env` file

## How do I run with 'DEBUG=False' in dev ?

Add in `conf/settings/local.py`
```console
DEBUG = False
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
```

Run the `development` web server

https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#cmdoption-runserver-insecure
```console
python manage.py runserver 0.0.0.0:8000 --insecure
```
