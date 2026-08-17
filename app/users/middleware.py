from allauth.mfa.utils import is_mfa_enabled
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

# Path prefixes a staff user must still be able to reach while enrolling in MFA
# (allauth account/login/logout pages and the MFA setup pages themselves).
EXEMPT_PATH_PREFIXES = (
    "/accounts/",
    "/django-admin/logout/",
)


class MFARequiredMiddleware:
    """Force staff users to enrol in MFA before using the Wagtail admin.

    Replaces the enforcement previously provided by `wagtail-2fa`'s
    `VerifyUserMiddleware`, using `django-allauth`'s MFA app instead.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._requires_mfa_setup(request):
            return redirect(reverse("mfa_index"))
        return self.get_response(request)

    def _requires_mfa_setup(self, request):
        if not getattr(settings, "MFA_REQUIRED", True):
            return False

        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return False

        if request.path.startswith(EXEMPT_PATH_PREFIXES):
            return False

        return not is_mfa_enabled(user)
