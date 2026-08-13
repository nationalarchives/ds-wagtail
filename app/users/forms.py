from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail.users.forms import UserCreationForm, UserEditForm


class UniqueEmailFormMixin:
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not email:
            return email

        user_model = get_user_model()
        existing_users = user_model._default_manager.filter(
            **{f"{user_model.get_email_field_name()}__iexact": email}
        )
        if self.instance.pk:
            existing_users = existing_users.exclude(pk=self.instance.pk)

        if existing_users.exists():
            raise ValidationError(
                _("This email address is already in use by another account.")
            )

        return email


class CustomUserCreationForm(UniqueEmailFormMixin, UserCreationForm):
    pass


class CustomUserEditForm(UniqueEmailFormMixin, UserEditForm):
    pass
