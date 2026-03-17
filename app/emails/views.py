from types import SimpleNamespace

from django.http import HttpResponse
from django.shortcuts import render
from django.template import engines


def email(request):

    context = {
        "uid": "Mg",
        "token": "set-password-preview-token",
        "protocol": request.scheme,
        "domain": request.get_host(),
        "user": SimpleNamespace(
            USERNAME_FIELD="username",
            get_username=lambda: "MyUsername",
        ),
    }

    template = engines["jinja2"].get_template(
        "/wagtailadmin/account/password_reset/email.html"
    )
    return HttpResponse(template.render(context, request=request))
