from django import template

register = template.Library()

from ..models import RecordPage


@register.simple_tag
def is_page_current_item_in_hierarchy(page: RecordPage, hierarchy_item: dict):
    """Checks whether given page matches item from a record's hierarchy"""
    return page.reference_number == hierarchy_item["reference_number"]
