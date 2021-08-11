from dataclasses import dataclass

from django.db import models

from wagtail.core.models import Page, Site

from ..ciim.models import SearchManager, MediaManager
from .transforms import transform_record_page_result, transform_image_result


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
    origination_date = models.TextField()
    legal_status = models.TextField()
    held_by = models.TextField(blank=True)
    is_digitised = models.BooleanField(default=False)
    parent = models.JSONField(null=True)
    hierarchy = models.JSONField(null=True)
    media_reference_id = models.UUIDField(null=True)
    availablility_access_display_label = models.TextField()
    availablility_access_closure_label = models.TextField()
    availablility_delivery_condition = models.TextField()
    availablility_delivery_surrogates = models.JSONField(null=True)

    def __init__(self, *args, **kwargs):
        """Override to add Kong response data to instance for debugging.

        The Django docs advice against overriding the __init__ method, due to
        the risk of the object not being persiable.

        This risk is mitagated due to the use of the RecordPage as a container
        to hold external data and should never be editable in the admin.

        https://docs.djangoproject.com/en/3.2/ref/models/instances/
        """
        self._debug_kong_result = kwargs.pop("_debug_kong_result", None)

        super().__init__(*args, **kwargs)

    def get_site(self):
        """Override to return the Site instance despite this page not belonging to the CMS.

        Site is used by base.html to add the site name to the page's <title>
        """
        return Site.objects.first()

    def __str__(self):
        return f"{self.title} ({self.iaid})"


"""Assign a search manager to the RecordPage

SearchManager exposes a similar interface to Django's model.Manager but 
results are fetched from the Kong API instead of from a DB

Transform function is used to transform a raw Elasticsearch response into a 
dictionary to pass to the Model's __init__.
"""
RecordPage.search = SearchManager(RecordPage)
RecordPage.transform = transform_record_page_result


@dataclass
class Image:
    """Represents an image item returned by Kong."""

    location: str


"""Assign a search manager to the Image

SearchManager exposes a similar interface to Django's model.Manager but 
results are fetched from the Kong API instead of from a DB

Transform function is used to transform a raw Elasticsearch response into a 
dictionary to pass to the Model's __init__.
"""
Image.search = SearchManager(Image)
Image.media = MediaManager(Image)
Image.transform = transform_image_result
