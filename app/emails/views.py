from types import SimpleNamespace
from django.shortcuts import render

def email(request):

    context = {
        "uid": "Mg",
        "token": "set-password-preview-token",
        "protocol": request.scheme,
        "domain": request.get_host(),
        "user": SimpleNamespace(
            USERNAME_FIELD="username",
            get_username="MyUsername",
        ),
    }

    return render(request, "wagtailadmin/account/password_reset/email.html", context)
