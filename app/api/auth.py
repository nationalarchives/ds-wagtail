from app.api.models import APIToken
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header


class TokenUser:
    """A simple user-like object for token authentication without a real user."""

    is_authenticated = True
    is_active = True
    is_anonymous = False

    def __init__(self, token):
        self.token = token

    def __str__(self):
        return f"TokenUser({self.token.name})"


class CustomTokenAuthentication(TokenAuthentication):
    model = APIToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _(
                "Invalid token header. Token string should not contain invalid characters."
            )
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.active:
            raise exceptions.AuthenticationFailed(_("Token inactive or deleted."))

        # Return a token user for service-to-service authentication
        return (TokenUser(token), token)
