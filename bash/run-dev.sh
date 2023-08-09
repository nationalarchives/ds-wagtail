#!/bin/bash

poetry run python /app/manage.py createsuperuser
poetry run python /app/manage.py migrate
poetry run python /app/manage.py runserver 0.0.0.0:8000
