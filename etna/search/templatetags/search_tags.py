import datetime
import logging

from typing import Union

from django import template
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe

import bleach

register = template.Library()
logger = logging.getLogger(__name__)


@register.filter
def record_detail(record: dict, key: str) -> str:
    """Fetch an item from a record's details template.

    Django templates don't allow access to keys or attributes prefixed with _

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """
    try:
        return record["_source"]["@template"]["details"][key]
    except KeyError:
        return ""


def record_highlight(record: dict, key: str) -> str:
    """
    Fetch a key for a record, either from the highlight dict, or the details template and strip all HTML apart from <mark>.
    """
    try:
        value = record["highlight"][f"@template.details.{key}"]
    except KeyError:
        try:
            value = record["_source"]["@template"]["details"][key]
        except KeyError:
            return ""

    if not value:
        return ""
    if isinstance(value, (list, tuple)):
        value = value[0]

    return mark_safe(bleach.clean(value, tags=["mark"], strip=True))


@register.filter
def record_title(record: dict) -> str:
    """
    Fetch the title for a record, either from the highlight dict, or the details template.
    """
    return record_highlight(record, "summaryTitle")


@register.filter
def record_description(record: dict) -> str:
    """
    Fetch the description for a record, either from the highlight dict, or the details template.
    """
    return record_highlight(record, "description")


@register.filter
def interpretive_detail(record: dict, key: str) -> str:
    """Fetch an item from a an interpretive records source object.

    Django templates don't allow access to keys or attributes prefixed with _

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """

    try:
        detail = record["_source"]["source"][key]
    except KeyError:
        return ""

    if isinstance(detail, (list, tuple)):
        try:
            return detail[0]
        except IndexError:
            return ""
    else:
        return detail


@register.filter
def record_score(record) -> str:
    """Output a record's score.

    Django templates don't allow access to keys or attributes prefixed with _

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """
    return record.get("_score")


@register.simple_tag(takes_context=True)
def query_string_include(context, key: str, value: Union[str, int]) -> str:
    """Add key, value to current query string."""

    request = context["request"]

    query_dict = request.GET.copy()
    query_dict[key] = value

    return query_dict.urlencode()


@register.simple_tag(takes_context=True)
def query_string_exclude(context, key: str, value: Union[str, int]) -> str:
    """Remove matching entry from current query string."""

    request = context["request"]

    query_dict = request.GET.copy()
    items = query_dict.getlist(key, [])
    query_dict.setlist(key, [i for i in items if i != str(value)])

    return query_dict.urlencode()


@register.filter
def include_hidden_fields(visible_field_names, form) -> str:
    """
    Returns automatically generated html hidden fields for the input form.
    The hidden fields are derived from the input form less the visible field names.
    A random suffix is applied to html id allowing the same form to be rendered
    multiple times without field ID clashes.
    """
    html = ""
    visible_field_list = visible_field_names.split()
    for field in form.fields:
        if field not in visible_field_list:
            if value := form.cleaned_data[field]:
                if isinstance(value, (str, int)):
                    html += f""" <input type="hidden" name="{field}" value="{value}" id="id_{field}_{get_random_string(3)}"> """
                elif isinstance(value, list):
                    for value_in_list in value:
                        html += f""" <input type="hidden" name="{field}" value="{value_in_list}" id="id_{field}_{get_random_string(3)}"> """
                elif isinstance(value, datetime.datetime):
                    html += f""" <input type="hidden" name="{field}" value="{value.date()}" id="id_{field}_{get_random_string(3)}"> """
                else:
                    logger.debug(
                        f"Type {type(value)} of the field-{field}'s value not supported in include_hidden_fields."
                    )
    return mark_safe(html)
