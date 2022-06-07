from typing import Any, Dict, Union

from django import template
from django.urls import NoReverseMatch, reverse

from ..field_labels import FIELD_LABELS
from ..models import Record

register = template.Library()


@register.simple_tag
def record_url(record: Union[Record, Dict[str, Any]]) -> str:
    """
    Return the URL for the provided `record` dict; which could either be a
    full/transformed result from the fetch() endpoint, OR a raw result from
    the search() endpoint.
    """

    if iaid := record.get("iaid"):
        try:
            return reverse("details-page-machine-readable", kwargs={"iaid": iaid})
        except NoReverseMatch:
            pass
    if ref := record.get("reference_number", record.get("referenceNumber")):
        try:
            return reverse(
                "details-page-human-readable", kwargs={"reference_number": ref}
            )
        except NoReverseMatch:
            pass
    if url := record.get("sourceUrl"):
        return url
    try:
        # Assume `record` is an un-transformed search result
        return record_url(record["_source"]["@template"]["details"])
    except KeyError:
        return ""


@register.simple_tag
def is_page_current_item_in_hierarchy(page: Record, hierarchy_item: dict):
    """Checks whether given page matches item from a record's hierarchy"""
    return page.reference_number == hierarchy_item["reference_number"]


@register.filter
def as_label(record_field_name: str) -> str:
    """returns human readable label for pre configured record field name, otherwise Invalid name"""
    return FIELD_LABELS.get(record_field_name, "UNRECOGNISED FIELD NAME")
