#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

    try:
        if sys.argv[1] == "test":
            os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
    except IndexError:
        # No arguments passed to manage.py
        ...

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


