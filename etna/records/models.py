from django.db import models

from wagtail.core.models import Page

from ..ciim.models import SearchManager


class RecordPage(Page):
    """Non-creatable page used to render record data in templates.

    This stub page allows us to use common templates to render external record
    data as though the data was fetched from the CMS.

    see: views.record_page_view
    """

    is_creatable = False

    iaid = models.TextField()
    reference_number = models.TextField()
    closure_status = models.TextField()
    created_by = models.TextField()
    description = models.TextField()
    arrangement = models.TextField(blank=True)
    date_start = models.IntegerField()
    date_end = models.IntegerField()
    date_range = models.TextField()
    legal_status = models.TextField()
    is_digitised = models.BooleanField(default=False)
    parent = models.JSONField(null=True)

    search = SearchManager("records.RecordPage")

    def __str__(self):
        return f"{self.title} ({self.iaid})"
