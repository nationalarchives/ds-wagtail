from django import template

from ..field_labels import FIELD_LABELS
from ..models import Record

register = template.Library()


@register.simple_tag
def is_page_current_item_in_hierarchy(page: Record, hierarchy_item: dict):
    """Checks whether given page matches item from a record's hierarchy"""
    return page.reference_number == hierarchy_item["reference_number"]


@register.filter
def as_label(record_field_name: str) -> str:
    """returns human readable label for pre configured record field name, otherwise blank"""
    return FIELD_LABELS.get(record_field_name, "")
