from __future__ import annotations

import logging
import re

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Union

from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse
from django.utils.functional import cached_property

from ..analytics.mixins import DataLayerMixin
from ..ciim.models import APIModel
from ..ciim.utils import (
    NOT_PROVIDED,
    ValueExtractionError,
    extract,
    format_description_markup,
    format_link,
)
from .converters import IAIDConverter

logger = logging.getLogger(__name__)


class Record(DataLayerMixin, APIModel):
    """A 'lazy' data-interaction layer for record data retrieved from the Kong API"""

    def __init__(self, raw_data: Dict[str, Any]):
        """
        This method recieves the raw JSON data dict recieved from
        Kong and makes it available to the instance as `self._raw`.
        """
        self.score = raw_data.get("_score")
        self._raw = raw_data.get("_source") or raw_data

    @classmethod
    def from_api_response(cls, response: dict) -> Record:
        return cls(response)

    def __str__(self):
        return f"{self.title} ({self.iaid})"

    def get(self, key: str, default: Optional[Any] = NOT_PROVIDED):
        """
        Attempts to extract `key` from `self._raw` and return the value.

        Raises `ciim.utils.ValueExtractionError` if the value cannot be extracted.
        """
        if "." in key:
            return extract(self._raw, key, default)
        try:
            return self._raw[key]
        except KeyError as e:
            if default is NOT_PROVIDED:
                raise ValueExtractionError(str(e))
            return default

    @cached_property
    def template(self) -> Dict[str, Any]:
        return self.get("@template.details", default=self.get("@template.results", {}))

    @cached_property
    def highlights(self) -> Dict[str, Any]:
        return self.get("highlight", default={})

    @cached_property
    def iaid(self) -> str:
        """
        Return the "iaid" value for this record (if one is available).

        Raises `ValueExtractionError` when the raw data does not include
        any candidate values.

        Raises `ValueError` when the raw data includes a value where iaids
        are usually found, but the value is not a valid iaid.
        """
        try:
            candidate = self.template["iaid"]
        except KeyError:
            candidate = self.get("@admin.id")

        # value is not guaranteed to be a valid 'iaid', so we must
        # check it before returning it as one
        if not re.match(IAIDConverter.regex, candidate):
            raise ValueError(f"Value '{candidate}' from API is not a valid iaid.")
        return candidate

    def has_iaid(self) -> bool:
        """
        Returns `True` if a valid 'iaid' value can be extracted from the
        raw data for this record. Otherwise `False`.
        """
        try:
            self.iaid
        except (ValueExtractionError, ValueError):
            return False
        else:
            return True

    @cached_property
    def reference_number(self) -> str:
        """
        Return the "reference_number" value for this record (if one is available).

        Raises `ValueExtractionError` when the raw data does not include
        values in any of the expected positions.
        """
        try:
            return self.template["referenceNumber"]
        except KeyError:
            pass
        identifiers = self.get("identifier", ())
        for item in identifiers:
            try:
                return item["reference_number"]
            except KeyError:
                pass
        raise ValueExtractionError(
            f"'reference_number' could not be extracted from source data: {self._raw}"
        )

    def has_reference_number(self) -> bool:
        """
        Returns `True` if a 'reference_number' value can be extracted from the
        raw data for this record. Otherwise `False`.
        """
        try:
            self.reference_number
        except ValueExtractionError:
            return False
        else:
            return True

    @cached_property
    def url(self):
        """
        Return the "url" value for this record. This value is typically
        only present for 'interpretive' results from other websites.

        Raises `ValueExtractionError` when the raw data does not include
        values in any of the expected positions.
        """
        try:
            return self.template["sourceUrl"]
        except KeyError:
            raise ValueExtractionError(
                f"'url' could not be extracted from source data: {self._raw}"
            )

    def has_url(self) -> bool:
        """
        Returns `True` if a 'url' value can be extracted from the raw data
        for this record. Otherwise `False`.
        """
        try:
            self.url
        except ValueExtractionError:
            return False
        else:
            return True

    @cached_property
    def title(self) -> str:
        try:
            return self.highlights["@template.details.summaryTitle"]
        except KeyError:
            pass
        try:
            return self.template["summaryTitle"]
        except KeyError:
            pass
        return self.get("summary.title", default="")

    @cached_property
    def is_tna(self):
        for item in self.get("@datatype.group", ()):
            if item.get("value", "") == "tna":
                return True
        return False

    @cached_property
    def closure_status(self) -> str:
        try:
            return self.template["accessCondition"]
        except KeyError:
            self.get("availability.access.condition.value", default="")
        return

    @cached_property
    def arrangement(self) -> str:
        try:
            raw = self.template["arrangement"]
        except KeyError:
            raw = self.get("arrangement.value", default="")
        return format_description_markup(raw)

    @cached_property
    def legal_status(self) -> str:
        try:
            return self.template["legalStatus"]
        except KeyError:
            return self.get("legal.status", default="")

    @cached_property
    def is_digitised(self) -> bool:
        return self.get("digitised", default=False)

    @cached_property
    def availability_delivery_surrogates(self) -> str:
        return self.get("availability.delivery.surrogate", default="")

    @cached_property
    def media_reference_id(self) -> str:
        return self.get("multimedia.@admin.id", default="")

    @cached_property
    def catalogue_source(self) -> str:
        return self.get("source.value", default="")

    @property
    def raw_description(self) -> str:
        try:
            return self.highlights["@template.details.description"]
        except KeyError:
            pass
        try:
            return self.template["description"]
        except KeyError:
            pass
        description_items = self.get("description", ())
        for item in description_items:
            if item.get("type", "") == "description" or len(description_items) == 1:
                return item.get("value", "")
        return ""

    @cached_property
    def description(self) -> str:
        if raw := self.raw_description:
            return format_description_markup(raw)
        return ""

    @cached_property
    def held_by(self) -> str:
        return self.template.get("heldBy", "")

    @cached_property
    def origination_date(self) -> str:
        return self.template.get("dateCreated", "")

    @cached_property
    def level(self) -> str:
        return self.get("level.value", self.template.get("level", ""))

    @cached_property
    def level_code(self) -> int:
        return self.get("level.code", None)

    @cached_property
    def availability_delivery_condition(self) -> str:
        return self.template.get("deliveryOption", "")

    @property
    def availability_condition_category(self) -> str:
        return settings.AVAILABILITY_CONDITION_CATEGORIES.get(
            self.availability_delivery_condition, ""
        )

    @cached_property
    def repo_summary_title(self) -> str:
        return self.get("repository.summary.title", default="")

    @cached_property
    def repo_archon_value(self) -> str:
        for item in self.get("repository.identifier", ()):
            if item["type"] == "Archon number":
                return item.get("value", "")
        return ""

    @cached_property
    def parent(self) -> Union["Record", None]:
        if parent_data := self.get("parent.0", default=None):
            return Record(parent_data)

    @cached_property
    def hierarchy(self) -> Tuple["Record"]:
        for item in self.get("@hierarchy.0", default=()):
            if not item.get("identifier"):
                level = item.get("level", {})
                level_code = level.get("code", "")
                hierarchy = self.get("@hierarchy.0", ())
                if hierarchy != () and level_code != "":
                    previous_level_record = hierarchy[level_code-2]
                    previous_level_identifier = previous_level_record.get("identifier")[0]
                    previous_level_reference = previous_level_identifier.get("reference_number")
                    if level_code == 2:
                        reference_number = "Division within " + previous_level_reference
                    elif level_code == 4:
                        reference_number = "Sub-series within " + previous_level_reference
                    item["identifier"] = [{'primary': True, 'reference_number': reference_number, 'type': 'reference number', 'value': reference_number}]
        return tuple(
            Record(item)
            for item in self.get("@hierarchy.0", default=())
            if item.get("identifier")
        )

    @cached_property
    def next_record(self) -> Union["Record", None]:
        if next := self.get("@next", default=None):
            return Record(next)

    @cached_property
    def previous_record(self) -> Union["Record", None]:
        if prev := self.get("@previous", default=None):
            return Record(prev)

    @cached_property
    def topics(self) -> Tuple[Dict[str, str]]:
        return_value = []
        for item in self.get("topic", default=()):
            topic_title = ""
            try:
                topic_title = item.get["name"][0]["value"]
            except (KeyError, IndexError):
                topic_title = extract(item, "summary.title")
            if topic_title:
                return_value.append({"title": topic_title})
        return tuple(return_value)

    @cached_property
    def related_records(self) -> Tuple["Record"]:
        return tuple(
            Record(item)
            for item in self.get("related", default=())
            if extract(item, "@link.relationship.value", default="") == "related"
        )

    @cached_property
    def related_articles(self) -> Tuple["Record"]:
        return tuple(
            Record(item)
            for item in self.get("related", default=())
            if item.get("summary")
            and extract(item, "@admin.source", default="") == "wagtail-es"
        )

    @cached_property
    def related_materials(self) -> Tuple[Dict[str, Any]]:
        return tuple(
            dict(
                description=item.get("description", ""),
                links=list(format_link(val) for val in item.get("links", ())),
            )
            for item in self.template.get("relatedMaterials", ())
        )

    def get_gtm_content_group(self) -> str:
        """
        Overrides DataLayerMixin.get_gtm_content_group() to
        return content group otherwise the name of the class.
        """
        if self.catalogue_source == "CAT":
            return "Catalogue: The National Archives"
        elif self.catalogue_source == "ARCHON":
            return "Catalogue: Archive Details"
        elif self.catalogue_source:
            return "Catalogue: Other Archive Records"
        else:
            return self.__class__.__name__

    @property
    def custom_dimension_11(self) -> str:
        if self.repo_archon_value and self.repo_summary_title:
            return self.repo_archon_value + " - " + self.repo_summary_title
        else:
            return "Held by not available"

    @property
    def custom_dimension_12(self) -> str:
        if self.level_code and self.level:
            return f"Level {self.level_code} - {self.level}"
        return ""

    @property
    def custom_dimension_13(self) -> str:
        for ancestor in self.hierarchy:
            if (
                ancestor.level_code == 3
                and ancestor.has_reference_number()
                and ancestor.title
            ):
                return f"{ancestor.reference_number} - {ancestor.title}"
        return ""

    @property
    def custom_dimension_14(self) -> str:
        if self.has_reference_number() and self.title:
            return f"{self.reference_number} - {self.title}"
        return ""

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Returns data to be included in the Google Analytics datalayer when
        rendering this record.

        Override this method on subclasses to add data that is relevant to a
        specific record type.
        """

        data = super().get_datalayer_data(request)
        data.update(
            contentGroup1=self.get_gtm_content_group(),
            customDimension3="record detail",
            customDimension11=self.custom_dimension_11,
            customDimension12=self.custom_dimension_12,
            customDimension13=self.custom_dimension_13,
            customDimension14=self.custom_dimension_14,
            customDimension15=self.catalogue_source,
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
