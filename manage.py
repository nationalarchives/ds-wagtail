#!/usr/bin/env python
import os
import sys

# THIS FILE IS NOT USED INSIDE DOCKER CONTAINERS - THIS IS USED INSTEAD:
# https://github.com/nationalarchives/docker/blob/main/docker/tna-python-django/lib/manage.py


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.develop")

    try:
        if sys.argv[1] == "test":
            # TEST CONFIG IS USED IN CI/CD
            os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
    except IndexError:
        # No arguments passed to manage.py
        ...

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
