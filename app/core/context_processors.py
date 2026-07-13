from django.conf import settings


def settings_vars(request):
    MEDIA_PAGE_URL = getattr(settings, "MEDIA_PAGE_URL", "")
    return {
        "ENVIRONMENT_NAME": getattr(settings, "ENVIRONMENT_NAME", ""),
        "BUILD_VERSION": getattr(settings, "BUILD_VERSION", ""),
        "IMAGE_PAGE_URL": MEDIA_PAGE_URL + "/image/",
        "VIDEO_PAGE_URL": MEDIA_PAGE_URL + "/video/",
        "AUDIO_PAGE_URL": MEDIA_PAGE_URL
        + "/video/",  # TODO: Update to /audio/ when implemented in frontend
    }
