#!/bin/bash

poetry run python /app/manage.py migrate
# poetry run python /app/manage.py createsuperuser --no-input
poetry run python /app/manage.py runserver 0.0.0.0:8080
