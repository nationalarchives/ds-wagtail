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

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.active:
            raise exceptions.PermissionDenied(_("Token inactive or deleted."))
    
        # Return a dummy TokenUser here - this is to avoid needing a real user model tied to the token
        return (TokenUser(token), token)
