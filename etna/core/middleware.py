import datetime
import logging

from django.conf import settings
from django.template.response import SimpleTemplateResponse

logger = logging.getLogger(__name__)


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
        Maintenanc Mode is overridden with MAINTENENCE_MODE_ALLOW_IPS
        """
        if settings.MAINTENANCE_MODE:
            # check override maintenance mode
            if get_client_ip(request) not in settings.MAINTENENCE_MODE_ALLOW_IPS:
                kwargs = {"template": "503.html", "status": 503}
                if maintenance_mode_ends := settings.MAINTENENCE_MODE_ENDS:
                    # Evaluate only if config is set
                    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Date, example "Wed, 21 Oct 2015 07:28:00 GMT"
                    HTTP_HEADER_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
                    try:
                        end_datetime = datetime.datetime.fromisoformat(
                            maintenance_mode_ends
                        )
                    except ValueError:
                        end_datetime = None
                        logger.debug(
                            f"settings.MAINTENENCE_MODE_ENDS={maintenance_mode_ends} is not iso format to add to Retry-After header."
                        )

                    if end_datetime:
                        kwargs.update(
                            {
                                "headers": {
                                    "Retry-After": end_datetime.strftime(
                                        HTTP_HEADER_FORMAT
                                    )
                                }
                            }
                        )
                return SimpleTemplateResponse(**kwargs).render()

        response = self.get_response(request)

        return response
