#!/bin/bash
chmod a+x bash/dev-watch.sh
./bash/dev-watch.sh &
poetry run python manage.py collectstatic --no-input
poetry run python manage.py migrate
poetry run python manage.py runserver 0.0.0.0:8000