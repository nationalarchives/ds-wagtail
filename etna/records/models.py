from dataclasses import dataclass, field

from django.conf import settings
from django.urls import reverse

from wagtail.core.models import Site

from ..ciim.models import MediaManager, SearchManager
from .transforms import transform_image_result, transform_record_result


@dataclass
class Record:
    """Non-creatable page used to render record data in templates.

    This stub page allows us to use common templates to render external record
    data as though the data was fetched from the CMS.

    see: views.record_detail_view
    """

    iaid: str
    title: str
    reference_number: str
    legal_status: str

    created_by: str = ''
    description: str = ''
    origination_date: str = ''
    closure_status: str = ""
    availability_access_display_label: str = ""
    availability_access_closure_label: str = ""
    availability_delivery_condition: str = ""
    arrangement: str = ""
    held_by: str = ""
    is_digitised: bool = False
    parent: dict = field(default_factory=dict)
    hierarchy: dict = field(default_factory=dict)
    media_reference_id: str = ""
    availability_delivery_surrogates: dict = field(default_factory=dict)
    topics: dict = field(default_factory=dict)
    next_record: dict = field(default_factory=dict)
    previous_record: dict = field(default_factory=dict)
    related_records: dict = field(default_factory=dict)
    related_articles: dict = field(default_factory=dict)

    _debug_kong_result: dict = field(default_factory=dict)

    def get_site(self):
        """Override to return the Site instance despite this page not belonging to the CMS.

        Site is used by base.html to add the site name to the page's <title>
        """
        return Site.objects.first()

    def __str__(self):
        return f"{self.title} ({self.iaid})"


"""Assign a search manager to Record

SearchManager exposes a similar interface to Django's model.Manager but
results are fetched from the Kong API instead of from a DB

Transform function is used to transform a raw Elasticsearch response into a
dictionary to pass to the Model's __init__.
"""
Record.search = SearchManager(Record)
Record.transform = transform_record_result


@dataclass
class Image:
    """Represents an image item returned by Kong."""

    location: str
    # Sort position of this image. Used to create the image-viewer URL
    # and to fetch this particular image from a series of images.
    # sort is an str that contains an int with a leading zero if less
    # than ten.
    sort: str
    thumbnail_location: str

    @property
    def thumbnail_url(self):
        """Use thumbnail URL is available, otherwise fallback to image-serve."""
        if self.thumbnail_location:
            return f"{settings.KONG_IMAGE_PREVIEW_BASE_URL}{self.thumbnail_location}"
        elif self.location:
            return reverse("image-serve", kwargs={"location": self.location})


"""Assign a search manager to the Image

SearchManager exposes a similar interface to Django's model.Manager but
results are fetched from the Kong API instead of from a DB

Transform function is used to transform a raw Elasticsearch response into a
dictionary to pass to the Model's __init__.
"""
Image.search = SearchManager(Image)
Image.media = MediaManager(Image)
Image.transform = transform_image_result
