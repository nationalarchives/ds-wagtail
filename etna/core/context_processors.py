from django.conf import settings


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
