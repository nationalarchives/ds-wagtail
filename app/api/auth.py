from app.api.models import APIToken
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


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

        # Return None here in place of the user object, as we're not assigning tokens to user accounts
        return (None, token)
