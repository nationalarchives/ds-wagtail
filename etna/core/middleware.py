import json
import logging
from urllib.parse import unquote

from django.conf import settings
from django.http import HttpRequest
from django.template.response import TemplateResponse

logger = logging.getLogger(__name__)

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Date, example "Wed, 21 Oct 2015 07:28:00 GMT"
HTTP_HEADER_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class InterpretCookiesMiddleware:
    exclude_paths = (
        "/admin/",
        "/django-admin/",
        "/documents/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def apply_to_request(self, request: HttpRequest) -> bool:
        for path in self.exclude_paths:
            if request.path.startswith(path):
                return False
        return True

    def process_template_response(
        self, request: HttpRequest, response: TemplateResponse
    ) -> TemplateResponse:
        # Exit early if the response shouldn't be modified
        if not self.apply_to_request(request):
            return response

        # Disable cookie by default
        cookies_permitted = False
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

        # Ensure context_data is not None
        if response.context_data is None:
            response.context_data = {}

        # Update context_data to reflect preferences
        response.context_data.update(
            cookies_permitted=cookies_permitted,
            show_cookie_notice=bool(
                settings.FEATURE_COOKIE_BANNER_ENABLED
                and "dontShowCookieNotice" not in request.COOKIES
            ),
        )
        return response
