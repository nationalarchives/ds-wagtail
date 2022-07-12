from django.conf import settings
from django.db import models


class IDPProfile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="idp_profiles", on_delete=models.CASCADE
    )
    provider_name = models.CharField(max_length=100, db_index=True)
    provider_user_id = models.CharField(max_length=100, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider_name", "provider_user_id"], name="idp_unique"
            ),
        ]
