import json
from urllib.parse import unquote

from django.conf import settings
from django.shortcuts import render


def get_context(request):
    # Disable cookie by default
    cookies_permitted = True
    if cookies_policy := request.COOKIES.get("cookies_policy", None):
        try:
            # Permit cookies if user has agreed
            cookies_permitted = json.loads(unquote(cookies_policy))["usage"] is True
        except (
            json.decoder.JSONDecodeError,  # value is not valid json
            TypeError,  # decoded json isn't a dict
            KeyError,  # dict doesn't contain 'usage'
            ValueError,  # 'usage' is something other than 'true'
        ):
            # Swallow above errors and leave 'cookies_permitted' as False
            pass
    # Update context_data to reflect preferences
    if_cookie_notice = bool(
        settings.FEATURE_COOKIE_BANNER_ENABLED
        and "dontShowCookieNotice" not in request.COOKIES
    )
    context = {
        "cookies_permitted": cookies_permitted,
        "show_cookie_notice": if_cookie_notice,
    }
    return context


def custom_500_error_view(request):
    context = get_context(request)
    response = render(request, "500.html", context=context)
    response.status_code = 500
    return response


def custom_503_error_view(request):
    context = get_context(request)
    response = render(request, "503.html", context=context)
    response.status_code = 503
    return response


def custom_404_error_view(request, exception=None):
    context = get_context(request)
    response = render(request, "404.html", context=context)
    response.status_code = 404
    return response
