# Using DJANGO-DEBUG-TOOLBAR in Dev

The toolbar is enabled for these variable settings which is default in dev.
```console
DEBUG = True
DEBUG_TOOLBAR_ENABLED = True
```
Alternative variable settings in files - [`.env`] or [`local.py`]
# Running DEBUG=False in Dev 
[`local.py`] file
```console
DEBUG = False
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
```

https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#cmdoption-runserver-insecure
Run
```console
python manage.py runserver 0.0.0.0:8000 --insecure
```

# Local development gotchas

This page lists common local development issues and how do resolve them.

## Brief description of problem

Solution description goes here.
