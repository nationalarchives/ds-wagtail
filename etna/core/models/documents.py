import re

from django.db import models

from wagtail.documents.models import AbstractDocument, Document


class CustomDocument(AbstractDocument):
    extent = models.CharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

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

    admin_form_fields = Document.admin_form_fields + (
        "extent",
        "description",
    )
