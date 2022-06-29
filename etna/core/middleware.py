from django.conf import settings
from django.template.response import SimpleTemplateResponse


def get_client_ip(request):
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
        if settings.MAINTENANCE_MODE:
            if get_client_ip(request) not in settings.MAINTENENCE_MODE_ALLOW_IPS:
                return SimpleTemplateResponse(template="503.html", status=503).render()

        response = self.get_response(request)

        return response
