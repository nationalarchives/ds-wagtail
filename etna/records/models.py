from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse

from ..analytics.mixins import DataLayerMixin
from ..ciim.models import APIModel
from .transforms import transform_record_result


@dataclass
class Record(DataLayerMixin, APIModel):
    """Non-creatable page used to render record data in templates.

    This stub page allows us to use common templates to render external record
    data as though the data was fetched from the CMS.

    see: views.record_detail_view
    """

    iaid: str
    title: str
    reference_number: str

    legal_status: str = ""
    created_by: str = ""
    description: str = ""
    origination_date: str = ""
    closure_status: str = ""
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
    datalayer_data: dict = field(default_factory=dict)

    _debug_kong_result: dict = field(default_factory=dict)

    def __str__(self):
        return f"{self.title} ({self.iaid})"

    @classmethod
    def from_api_response(cls, response: dict) -> Record:
        return cls(**transform_record_result(response))

    @property
    def availability_condition_category(self) -> str:
        return settings.AVAILABILITY_CONDITION_CATEGORIES.get(
            self.availability_delivery_condition, ""
        )

    def get_gtm_content_group(self) -> str:
        """
        Overrides DataLayerMixin.get_gtm_content_group() to
        return content group otherwise the name of the class.
        """
        return self.datalayer_data.get("contentGroup1", self.__class__.__name__)

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Returns data to be included in the Google Analytics datalayer when
        rendering this record.

        Override this method on subclasses to add data that is relevant to a
        specific record type.
        """
        data = super().get_datalayer_data(request)
        data.update(
            customDimension16=self.availability_condition_category,
            customDimension17=self.availability_delivery_condition,
        )
        return data


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
