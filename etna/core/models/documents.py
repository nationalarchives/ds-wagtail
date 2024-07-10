from django.db import models

from wagtail.documents.models import AbstractDocument, Document


class CustomDocument(AbstractDocument):
    extent = models.CharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    @property
    def pretty_file_size(self):
        suffixes = ["B", "KB", "MB", "GB"]
        i = 0
        pretty_file_size = self.file_size
        while pretty_file_size >= 1000 and i < len(suffixes) - 1:
            pretty_file_size /= 1000
            i += 1
        return f"{pretty_file_size:.1f}{suffixes[i]}"

    admin_form_fields = Document.admin_form_fields + (
        "extent",
        "description",
    )
