from uuid import uuid4

from django.db import models


class APIToken(models.Model):
    """
    A custom API token to enable API tokens
    to be generated for services to access the API.
    """

    name = models.CharField(max_length=100, unique=True)
    key = models.CharField(default=uuid4, max_length=40, unique=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
