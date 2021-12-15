from allauth.account import app_settings
from allauth.account.forms import LoginForm
from allauth.account.utils import perform_login
from django import forms
from django.contrib.auth import authenticate


class AxesLoginForm(LoginForm):

    def login(self, *args, **kwargs):
        self.user = kwargs['user']
        self.request = args[0]
        ret = perform_login(
            self.request,
            self.user,
            email_verification=app_settings.EMAIL_VERIFICATION,
            redirect_url=None,
            email=self.user.email,
        )
        remember = app_settings.SESSION_REMEMBER
        if remember is None:
            remember = self.cleaned_data["remember"]
        if remember:
            self.request.session.set_expiry(app_settings.SESSION_COOKIE_AGE)
        else:
            self.request.session.set_expiry(0)
        return ret

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['login'].error_messages = {'required': 'The email field is required'}

        self.fields['password'].error_messages = {'required': 'The password field is required'}

    def user_credentials(self):
        credentials = super().user_credentials()
        credentials['login'] = credentials.get('email') or credentials.get('username')
        return credentials

    def clean(self):
        super(LoginForm, self).clean()
        if self._errors:
            return

    def add_errors(self, **kwargs):
        self.request = kwargs.pop("request", None)
        if hasattr(self.request, 'axes_locked_out'):
            if self.request.axes_locked_out:
                self.add_error(None, "Locked User")
            else:
                self.add_error(None, "Invalid username or password")
        else:
            self.add_error(None, "Error")

