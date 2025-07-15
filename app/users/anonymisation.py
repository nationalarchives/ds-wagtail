import uuid

from birdbath.processors import BaseModelAnonymiser
from django.contrib.auth.models import User


class UserAnonymiser(BaseModelAnonymiser):
    model = User

    # generate random replacement values for these fields
    anonymise_fields = [
        "first_name",
        "last_name",
        "email",
        "password",
        "username",
    ]

    def generate_email(self, field, obj):
        # Use the fake 'first_name' and 'last_name' to create a new value
        return f"{obj.first_name.lower()}.{obj.last_name.lower()}@example.com"

    def generate_username(self, field, obj):
        # Generate a more constistently-formatted unique value with a
        # reasonable length that doesn't break the listing UI in Wagtail
        return uuid.uuid4()
