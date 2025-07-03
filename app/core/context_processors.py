from django.conf import settings


def feature_flags(request):
    """
    Passes settings with the "FEATURE_" prefix through to template contexts,
    allowing conditional logic to be added to both Python and template code.
    Explicitly sets the values for each setting rather than using settings.__dict__ which gets cached
    """

    return {
        "FEATURE_COOKIE_BANNER_ENABLED": settings.FEATURE_COOKIE_BANNER_ENABLED,
        "FEATURE_DISABLE_JS_WHATS_ON_LISTING": settings.FEATURE_DISABLE_JS_WHATS_ON_LISTING,
    }


def settings_vars(request):
    return {
        "ENVIRONMENT_NAME": settings.ENVIRONMENT_NAME,
    }
