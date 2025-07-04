from allauth.account.adapter import DefaultAccountAdapter


class NoSelfSignupAccountAdapter(DefaultAccountAdapter):
    """NoSelfSignupAccountAdapter

    Override is_open_for_signup to prevent user self-signup.

    Ref: https://django-allauth.readthedocs.io/en/latest/advanced.html#custom-redirects
    """

    def is_open_for_signup(self, request):
        return False
