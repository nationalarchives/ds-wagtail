import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

logger = logging.getLogger(__name__)


# https://github.com/pennersr/django-allauth/blob/main/allauth/socialaccount/adapter.py
class OIDCAdapter(DefaultSocialAccountAdapter):
    # IT to control access via the Entra Enterprise Application (or appRole), Wagtail permissions remain managed in the CMS.
    def save_user(self, request, sociallogin, form=None):
        # Use the default user creation/update logic first
        user = super().save_user(request, sociallogin, form)

        extra = getattr(sociallogin.account, "extra_data", {}) or {}

        # TODO finish this properly

        try:
            if not user.email:
                # not this but this
                # email = user.mail | user.emailaddress
                # if not email:
                # make more specified rather than wasting work and assumptions
                for key in (
                    "email",
                    "mail",
                    "userPrincipalName",
                    "upn",
                    "preferred_username",
                    "emailaddress",
                ):
                    email = extra.get(key)
                    if isinstance(email, str) and "@nationalarchives.gov.uk" in email:
                        user.email = email
                        user.save(update_fields=["email"])

        except Exception:
            logger.exception("Error normalising email from OIDC claims")

        return user
