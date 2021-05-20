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

    catalogue_id = models.IntegerField()
    reference_number = models.IntegerField()
    closure_status = models.TextField()
    created_by = models.TextField()
    description = models.TextField()
    date_start = models.IntegerField()
    date_end = models.IntegerField()
    date_range = models.TextField()
    legal_status = models.TextField()

    search = SearchManager("records.RecordPage")
