import re

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.documents.models import AbstractDocument, Document


class CustomDocument(AbstractDocument):
    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
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

    @property
    def pretty_file_size(self):
        suffixes = ["B", "kB", "MB", "GB"]
        i = 0
        pretty_file_size = self.file_size
        while pretty_file_size >= 1000 and i < len(suffixes) - 1:
            pretty_file_size /= 1000
            i += 1
        return re.sub(
            r"\.0+$", "", f"{pretty_file_size:.{max(i - 1, 0)}f}{suffixes[i]}"
        )

    @property
    def full_url(self):
        return settings.WAGTAILADMIN_BASE_URL + self.url

    admin_form_fields = Document.admin_form_fields + (
        "extent",
        "description",
    )
