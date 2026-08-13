from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameModelBackend(ModelBackend):
    """Allows authentication with either the username or email address."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(get_user_model().USERNAME_FIELD)
        if username is None or password is None:
            return None

        user_model = get_user_model()
        try:
            user = user_model._default_manager.get(email__iexact=username)
        except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
            return super().authenticate(
                request, username=username, password=password, **kwargs
            )

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
