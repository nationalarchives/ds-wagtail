from django.conf import settings


def feature_flags(request):
    return {
        key: value
        for key, value in settings.__dict__.items()
        if key.startswith("FEATURE_")
    }
