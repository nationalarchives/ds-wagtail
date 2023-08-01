#!/bin/bash

if [ "$AUTO_START_SERVER" = true ] ; then
  chmod a+x ./bash/dev-watch.sh
  ./bash/dev-watch.sh &
  poetry run python manage.py migrate
  poetry run python manage.py runserver 0.0.0.0:8000
else
  tail -f /dev/null
fi
