from app.api.models import APIToken
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, TokenAuthentication


class DummyUser:
    """
    A dummy user class to represent token-authenticated requests that are not associated with a specific user account.
    This allows us to use DRF's authentication framework without requiring a user model for token authentication.
    """

    is_authenticated = True


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

        # Return a DummyUser instance in place of the user object, as we're not assigning tokens to user accounts
        return (DummyUser(), token)


class UserAuthentication(BaseAuthentication):
    """
    This authentication class is used to allow the use of session
    authentication for users who log in via the Wagtail admin interface
    """

    def authenticate(self, request):
        # Check if the user is authenticated and is a staff member (i.e. has access to the Wagtail admin)
        user = getattr(getattr(request, "_request", None), "user", None)
        if not user or not user.is_authenticated:
            return None

        return (user, None)


class TokenOrUserAuthentication(BaseAuthentication):
    """
    Prefer token authentication; fall back to session user authentication.
    """

    def authenticate(self, request):
        token_auth = CustomTokenAuthentication()
        token_result = token_auth.authenticate(request)
        if token_result is not None:
            return token_result

        user_auth = UserAuthentication()
        return user_auth.authenticate(request)
