from django.db import models

from wagtail.documents.models import Document, AbstractDocument

class CustomDocument(AbstractDocument):
    extent = models.CharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    admin_form_fields = Document.admin_form_fields + (
        "extent",
        "description",
    )