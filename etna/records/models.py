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
    held_by = models.TextField(blank=True)
    is_digitised = models.BooleanField(default=False)
    parent = models.JSONField(null=True)
    hierarchy = models.JSONField(null=True)
    media_reference_id = models.UUIDField(null=True)

    search = SearchManager("records.RecordPage")

    def __init__(self, *args, **kwargs):
        """Override to add Kong response data to instance for debugging.

        The Django docs advice against overriding the __init__ method, due to
        the risk of the object not being persiable.

        This risk is mitagated due to the use of the RecordPage as a container
        to hold external data and should never be editable in the admin.

        https://docs.djangoproject.com/en/3.2/ref/models/instances/
        """
        self._debug_kong_result = kwargs.pop('_debug_kong_result', None)

        super().__init__(*args, **kwargs)


    def __str__(self):
        return f"{self.title} ({self.iaid})"
