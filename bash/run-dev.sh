#!/bin/bash

mkdir -p /app/templates/static/assets
cp -R /app/node_modules/@nationalarchives/frontend/nationalarchives/assets/* /app/templates/static/assets
poetry run python /app/manage.py runserver 0.0.0.0:8080
