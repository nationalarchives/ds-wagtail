from django.conf import settings
from django.shortcuts import render


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if settings.MAINTENANCE_MODE:
            return render(request, "503.html")

        response = self.get_response(request)

        return response
