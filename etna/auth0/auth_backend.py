from django.contrib.auth.backends import ModelBackend


class Auth0Backend(ModelBackend):
    """
    A backend that overrides the `authenticate()` method to prevent succesfull
    use with anything other than ``views.authorize()``, which specifies this
    as the ``backend`` for users when calling `django.contrib.auth.login()`
    (after successful authentication with Auth0).
    """

    def authenticate(self, request, **kwargs):
        return None
