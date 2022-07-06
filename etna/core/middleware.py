import logging

from datetime import datetime, timedelta
from urllib.parse import quote

from django.conf import settings
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


class SetDefaultCookiePreferencesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not settings.FEATURE_COOKIE_BANNER_ENABLED:
            return response
        cookie_name = "cookies_policy"
        if not request.COOKIES.get(cookie_name, None):
            expires = datetime.utcnow() + timedelta(days=90)
            value = '{"usage":false,"settings":false,"essential":true}'
            response.set_cookie(
                cookie_name,
                expires=expires,
                path="/",
                domain=settings.COOKIE_DOMAIN,
                value=quote(value),
            )
        return response
