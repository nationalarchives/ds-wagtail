import binascii
import datetime
import os

from django.db import models


class APIToken(models.Model):
    """
    A custom API token to enable API tokens
    to be generated for services to access the API.
    """

    name = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=40, unique=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        self.updated = datetime.datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.name
