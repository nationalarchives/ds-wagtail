from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import MultipleObjectsReturned


class EmailModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        email = kwargs.get(user_model.get_email_field_name()) or username

        if not email or password is None:
            return None

        try:
            user = user_model._default_manager.get(
                **{f"{user_model.get_email_field_name()}__iexact": email}
            )
        except (user_model.DoesNotExist, MultipleObjectsReturned):
            return None

        return (
            user
            if user.check_password(password) and self.user_can_authenticate(user)
            else None
        )
