from django.conf import settings


def settings_vars(request):
    return {
        "ENVIRONMENT_NAME": settings.ENVIRONMENT_NAME,
        "BUILD_VERSION": settings.BUILD_VERSION,
    }
