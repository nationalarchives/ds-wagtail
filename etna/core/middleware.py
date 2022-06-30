from django.conf import settings
from django.template.response import SimpleTemplateResponse

from etna.ciim.utils import get_date_for_retry_after_header


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
                if settings.MAINTENENCE_MODE_ENDS:
                    kwargs.update(
                        {
                            "headers": {
                                "Retry-After": get_date_for_retry_after_header(
                                    settings.MAINTENENCE_MODE_ENDS
                                )
                            }
                        }
                    )
                return SimpleTemplateResponse(**kwargs).render()

        response = self.get_response(request)

        return response
