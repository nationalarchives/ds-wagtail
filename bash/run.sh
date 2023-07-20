#!/bin/bash

poetry run python manage.py migrate
poetry run gunicorn config.wsgi:application --capture-output --workers 3 --threads 3 --log-level=DEBUG -b 0.0.0.0:8000
