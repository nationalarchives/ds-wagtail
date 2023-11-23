from django.conf import settings


def feature_flags(request):
    """
    Passes settings with the "FEATURE_" prefix through to template contexts,
    allowing conditional logic to be added to both Python and template code.
    Explicitly sets the values for each setting rather than using settings.__dict__ which gets cached
    """

    return {
        "FEATURE_RECORD_LINKS_GO_TO_DISCOVERY": settings.FEATURE_RECORD_LINKS_GO_TO_DISCOVERY,
        "FEATURE_DOWNLOAD_RECORD_LINKS_GO_TO_DISCOVERY": settings.FEATURE_DOWNLOAD_RECORD_LINKS_GO_TO_DISCOVERY,
        "FEATURE_BETA_BANNER_ENABLED": settings.FEATURE_BETA_BANNER_ENABLED,
        "FEATURE_COOKIE_BANNER_ENABLED": settings.FEATURE_COOKIE_BANNER_ENABLED,
        "FEATURE_PLATFORM_ENVIRONMENT_TYPE": settings.FEATURE_PLATFORM_ENVIRONMENT_TYPE,
        "FEATURE_FEEDBACK_MECHANISM_ENABLED": settings.FEATURE_FEEDBACK_MECHANISM_ENABLED,
    }
