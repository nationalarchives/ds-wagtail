from django import template

from ..models import Record
from ..field_labels import human_readable_labels

register = template.Library()


@register.simple_tag
def is_page_current_item_in_hierarchy(page: Record, hierarchy_item: dict):
    """Checks whether given page matches item from a record's hierarchy"""
    return page.reference_number == hierarchy_item["reference_number"]


@register.filter
def as_label(record_field_name: str) -> str:
    """returns human readable pre configured record/api field name, otherwise blank"""
    return human_readable_labels.get(record_field_name, "")
