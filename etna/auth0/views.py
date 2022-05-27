from urllib.parse import quote_plus, urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from authlib.integrations.django_client import OAuth

User = get_user_model()

oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def login(request):
    callback_url = reverse("account_authorize")
    if next := request.GET.get("next"):
        callback_url += "?" + urlencode(next)
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(callback_url)
    )


def authorize(request):
    token = oauth.auth0.authorize_access_token(request)
    user_info = token["userinfo"]
    user, created = User.objects.update_or_create(
        username=user_info["email"],
        defaults={
            "email": user_info["email"],
            "first_name": user_info.get("given_name"),
            "last_name": user_info.get("family_name"),
        },
    )
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])
    auth_login(request, user, backend="etna.auth0.auth_backend.Auth0Backend")
    return HttpResponseRedirect(request.GET.get("next") or "/")


def logout(request):
    auth_logout(request)
    redirect_to = "/"
    if settings.TERMINATE_SSO_SESSION_ON_LOGOUT:
        return redirect(
            f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
            + urlencode(
                {
                    "returnTo": request.build_absolute_uri(redirect_to),
                    "client_id": settings.AUTH0_CLIENT_ID,
                },
                quote_via=quote_plus,
            ),
        )
    else:
        return HttpResponseRedirect(redirect_to)
