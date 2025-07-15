"""
WSGI config for etna project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
from django.conf import settings
from django.core.wsgi import get_wsgi_application

if settings.VSC_DEBUGGER == True:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("Waiting for debugger attach...")
    debugpy.wait_for_client() # Debugger will pause the application until a client is attached
elif settings.PYC_DEBUGGER == True:
    import pydevd_pycharm
    pydevd_pycharm.settrace(
        'host.docker.internal',
        port=5678,
        stdoutToServer=True,
        stderrToServer=True,
        suspend=True
    )

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
