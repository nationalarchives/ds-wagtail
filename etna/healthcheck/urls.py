from django.http import HttpResponse
from django.urls import path


def healthcheck(request):
    return HttpResponse("ok")


app_name = "healthcheck"
urlpatterns = [
    path(
        "",
        healthcheck,
    ),
    path(
        "live/",
        healthcheck,
    ),
]
