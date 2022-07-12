from django.conf import settings


def globals(request):
    """
    Adds common setting (and potentially other values) to the context.
    """
    return {
        "MY_ACCOUNT_URL": settings.MY_ACCOUNT_URL,
        "REGISTER_URL": settings.REGISTER_URL,
    }


def feature_flags(request):
    """
    Makes any settings with the "FEATURE_" prefix available template contexts,
    allowing conditional logic to be added to both Python and template code.
    """
    return {
        key: value
        for key, value in settings.__dict__.items()
        if key.startswith("FEATURE_")
    }
