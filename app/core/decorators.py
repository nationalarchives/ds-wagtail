from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def setting_controlled_login_required(
    function=None,
    setting_name=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url=None,
):
    """
    Decorator for views that conditionally require login based on the value
    of a Django project setting (usually controlled via env vars),
    redirecting to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: not getattr(settings, setting_name) or u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
