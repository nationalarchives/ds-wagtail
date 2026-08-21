from django.db import models
from wagtail.documents.models import AbstractDocument, Document


class CustomDocument(AbstractDocument):
    title = models.CharField(
        max_length=255,
        verbose_name="title",
        help_text="The name of the document as it will appear on the webpage. Please format this in sentence case with spaces between the words. e.g. Preservation policy part one.",
    )
    extent = models.CharField(
        blank=True,
        null=True,
        help_text="The volume of the file so that users understand how much there is to consume. E.g. '3 pages' or '120 images'.",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="A short summary of what the document contains to help users understand what they are downloading.",
    )

    admin_form_fields = Document.admin_form_fields + (
        "extent",
        "description",
    )
