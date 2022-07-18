import json
import logging

from datetime import datetime
from urllib.parse import unquote

from django.conf import settings
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.template.response import SimpleTemplateResponse

from pytz import timezone

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


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Renders for a 503 if MAINTENANCE_MODE is set.
        Maintenance mode should be bypassed when the user's public IP address is present in  MAINTENENCE_MODE_ALLOW_IPS
        """
        if settings.MAINTENANCE_MODE:
            # check override maintenance mode
            if get_client_ip(request) not in settings.MAINTENENCE_MODE_ALLOW_IPS:
                kwargs = {"template": "503.html", "status": 503}
                if maintenance_mode_ends := settings.MAINTENENCE_MODE_ENDS:
                    # Evaluate only if config is set
                    try:
                        end_datetime = datetime.fromisoformat(maintenance_mode_ends)
                    except ValueError:
                        end_datetime = None
                        logger.debug(
                            f"settings.MAINTENENCE_MODE_ENDS={maintenance_mode_ends} is not iso format to add to Retry-After header."
                        )

                    if end_datetime:
                        # GMT is assumed for naive datetimes, but timezone-aware
                        # datetimes must be converted to GMT
                        if end_datetime.utcoffset() is not None:
                            end_datetime = end_datetime.astimezone(timezone("GMT"))

                        kwargs["headers"] = {
                            "Retry-After": end_datetime.strftime(HTTP_HEADER_FORMAT)
                        }
                return SimpleTemplateResponse(**kwargs).render()

        response = self.get_response(request)

        return response


class InterpretCookiesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_template_response(
        self, request: HttpRequest, response: TemplateResponse
    ) -> TemplateResponse:

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

        # Update context_data to reflect preferences
        response.context_data["cookies_permitted"] = cookies_permitted
        response.context_data["show_cookie_notice"] = bool(
            settings.FEATURE_COOKIE_BANNER_ENABLED and "dontShowCookieNotice" not in request.COOKIES
        )
        response.context_data["show_beta_banner"] = bool(
            settings.FEATURE_BETA_BANNER_ENABLED and "beta_banner_dismissed" not in request.COOKIES
        )
        return response
