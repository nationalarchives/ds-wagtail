from urllib.parse import quote_plus, urlencode, urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from authlib.integrations.django_client import OAuth

from etna.users.models import IDPProfile

User = get_user_model()

PROVIDER_NAME = "auth0"

oauth = OAuth()
oauth.register(
    PROVIDER_NAME,
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
        request.session["auth_success_url"] = next
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(callback_url)
    )


def register(request):
    callback_url = reverse("account_authorize")
    if next := request.GET.get("next"):
        request.session["auth_success_url"] = next
    return oauth.auth0.authorize_redirect(
        request,
        request.build_absolute_uri(callback_url),
        screen_hint="signup",
        prompt="login",
    )


def authorize(request):
    if success_url := request.session.get("auth_success_url"):
        parsed = urlparse(success_url)
        if parsed.netloc and parsed.netloc != request.META.get("HTTP_HOST"):
            success_url = "/"
    else:
        success_url = "/"

    token = oauth.auth0.authorize_access_token(request)
    user_info = token["userinfo"]
    user_id = user_info.get("user_id") or user_info.get("sub")
    now = timezone.now()

    try:
        # First, try to find a user with a matching profile
        profile = IDPProfile.objects.select_related("user").get(
            provider_name=PROVIDER_NAME, provider_user_id=user_id
        )
    except IDPProfile.DoesNotExist:
        # If no Django user was found, create a new one with a unique username
        candidate_username = user_info["nickname"][:150]
        username = candidate_username
        i = 1
        while User.objects.filter(username=username).exists():
            username = f"{candidate_username[:148]}{i}"
            i += 1

        user = User(
            username=username,
            email=user_info["email"],
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
        )
        user.set_unusable_password()
        user.save()

        # Finally, create the IDDProfile object to link the user to this login
        IDPProfile.objects.create(
            user=user,
            provider_name=PROVIDER_NAME,
            provider_user_id=user_id,
            last_login=now,
        )
    else:
        # Update the 'last_login' timestamp for the existing profile
        profile.last_login = now
        profile.save(update_fields=["last_login"])

        # Update local user to reflect any changes in auth0
        user = profile.user
        user.__dict__.update(
            email=user_info["email"],
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
        )

    # If email verification is required, reject access to non-verified emails
    if settings.AUTH0_EMAIL_VERIFICATION_REQUIRED and not user_info["email_verified"]:
        url = settings.AUTH0_VERIFY_EMAIL_URL
        if not url:
            return HttpResponseForbidden(
                "This service can only be used by users with a verified email address."
            )
        return redirect(url)

    auth_login(request, user, backend="etna.auth0.auth_backend.Auth0Backend")
    return HttpResponseRedirect(success_url)


def logout(request):
    success_url = settings.LOGOUT_REDIRECT_URL
    auth_logout(request)
    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(success_url),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )
