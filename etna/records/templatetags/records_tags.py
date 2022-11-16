from typing import Any, Dict, Union

from django import template
from django.conf import settings
from django.urls import NoReverseMatch, reverse

from etna.ciim.utils import ValueExtractionError

from ..field_labels import FIELD_LABELS
from ...ciim.constants import LevelKeys
from ..models import Record

register = template.Library()


@register.simple_tag
def record_url(
    record: Union[Record, Dict[str, Any]], is_editorial: bool = False
) -> str:
    """
    Return the URL for the provided `record` dict; which could either be a
    full/transformed result from the fetch() endpoint, OR a raw result from
    the search() endpoint.
    Handling of Iaid as priority to allow Iaid in disambiguation pages when
    returning more than one record
    """
    try:
        # Use Record property if available
        iaid = record.iaid
    except AttributeError:
        # 'record' is likely just a dict
        iaid = record.get("iaid")
    except (
        ValueExtractionError,  # Value was not present
        ValueError,  # Value was invalid
    ):
        iaid = None

    try:
        # Use Record property if available
        ref = record.reference_number
    except AttributeError:
        # 'record' is likely just a dict
        ref = record.get("reference_number", record.get("referenceNumber"))
    except ValueExtractionError:
        ref = None

    try:
        # Use Record property if available
        url = record.url
    except AttributeError:
        # 'record' is likely just a dict
        url = record.get("sourceUrl")
    except ValueExtractionError:
        url = None

    if iaid:
        if is_editorial and settings.FEATURE_RECORD_LINKS_GO_TO_DISCOVERY:
            return f"https://discovery.nationalarchives.gov.uk/details/r/{iaid}"
        try:
            return reverse("details-page-machine-readable", kwargs={"iaid": iaid})
        except NoReverseMatch:
            pass
    if ref:
        try:
            return reverse(
                "details-page-human-readable", kwargs={"reference_number": ref}
            )
        except NoReverseMatch:
            pass
    if url:
        return url
    try:
        # Assume `record` is an un-transformed search result
        return record_url(record["_source"]["@template"]["details"], is_editorial)
    except (TypeError, KeyError):
        return ""


@register.simple_tag
def is_page_current_item_in_hierarchy(page: Record, hierarchy_item: Record):
    """Checks whether given page matches item from a record's hierarchy"""
    return page.reference_number == hierarchy_item.reference_number


@register.filter
def as_label(record_field_name: str) -> str:
    """returns human readable label for pre configured record field name, otherwise Invalid name"""
    return FIELD_LABELS.get(record_field_name, "UNRECOGNISED FIELD NAME")


@register.simple_tag
def current_hierarchy_level(current_level_code: int) -> str:
    """returns human readable level"""
    return LevelKeys["LEVEL_"+current_level_code]