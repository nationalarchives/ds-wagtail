import datetime
import logging

from typing import Union

from django import template
from django.forms import Form
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe

from etna.ciim.constants import (
    COLLECTION_ATTR_FOR_ALL_BUCKETS,
    LONG_FILTER_PARAM_VALUES,
    PARENT_PARAM_VALUES,
    PREFIX_AGGS_PARENT_CHILD_KV,
    SEE_MORE_PREFIX,
    SEPERATOR,
    BucketKeys,
    SearchTabs,
)

register = template.Library()
logger = logging.getLogger(__name__)


@register.filter
def is_date(value) -> bool:
    """Return True if value is a date."""
    return isinstance(value, datetime.date)


@register.simple_tag(takes_context=True)
def query_string_include(context, key: str, value: Union[str, int]) -> str:
    """Add key, value to current query string."""

    request = context["request"]

    query_dict = request.GET.copy()
    query_dict[key] = value

    return query_dict.urlencode()


@register.simple_tag(takes_context=True)
def query_string_exclude(
    context, key: str, value: Union[str, int, datetime.date]
) -> str:
    """Remove matching entry from current query string."""

    request = context["request"]

    query_dict = request.GET.copy()

    if key in (
        "opening_start_date",
        "opening_end_date",
        "covering_date_from",
        "covering_date_to",
    ):
        # We're only ever dealing with single date values for these fields, so can
        # safely remove all date segments from the querystring regardless of
        # whether they match the supplied `value`
        query_dict.pop(f"{key}_0", None)
        query_dict.pop(f"{key}_1", None)
        query_dict.pop(f"{key}_2", None)
    else:
        items = query_dict.getlist(key, [])

        value = str(value)

        if value in PARENT_PARAM_VALUES:
            # remove parent and child aggs for that parent
            aggs = value.split(":")[0]
            filters = []
            for filter in items:
                if filter != value and not filter.startswith(
                    PREFIX_AGGS_PARENT_CHILD_KV.get(aggs)
                ):
                    filters.append(filter)
            query_dict.setlist(key, filters)
        else:
            query_dict.setlist(key, [filter for filter in items if filter != value])

    return query_dict.urlencode()


@register.simple_tag
def render_fields_as_hidden(
    form: Form,
    exclude: str = "",
    include: str = "",
    long_filter: bool = False,
) -> str:
    """
    Render the supplied `form`'s fields as hidden inputs. Used within a <form> tag
    to preserve state between requests when the same Django form is rendered in
    multiple places on the same page (with different visible fields each time).

    `form`: The Django form to render fields for.
    `exclude`: A space-separated string of field names to NOT be rendered as hidden.
    `include`: A space-separated string of field names to be rendered as hidden.
    `long_filter`: to exclude nested long filter value from the field
    """
    include_names = include.split()
    exclude_names = exclude.split()

    # Gather the relevant `BoundField` instances into a list
    boundfields = []
    for field in form:
        if include_names:
            if field.name in include_names:
                boundfields.append(field)
        elif field.name not in exclude_names:
            boundfields.append(field)

    # Utilize `BoundField.as_hidden()` to generate the return html
    html = ""
    for field in boundfields:
        if long_filter and field.name == COLLECTION_ATTR_FOR_ALL_BUCKETS:
            # to handle return to search
            hidden_fmt = """<input type="hidden" name="{field}" value="{value}" id="id_collection_{suffix}">"""
            for value in field.data:
                if value not in LONG_FILTER_PARAM_VALUES:
                    html += hidden_fmt.format(
                        field=field.name, value=value, suffix=get_random_string(3)
                    )
        else:
            html += field.as_hidden(
                # Add a random string to the field ID to avoid collisions with
                # the editable versions of fields on the same page
                attrs={"id": f"id_{field.name}_{get_random_string(3)}"}
            )
    return mark_safe(html)


@register.filter
def search_title(search_tab) -> str:
    """
    Returns title for search tab
    """
    if search_tab == SearchTabs.ALL.value:
        label = "All search results"
    elif search_tab == SearchTabs.CATALOGUE.value:
        label = "Search results"
    return label


@register.simple_tag
def extended_in_operator(lhs_operand, *rhs_operand_list) -> bool:
    """
    Input params are template tags
    Returns True when rhs_operand_list contains lhs_operand value, False otherwise
    """
    return (lhs_operand in rhs_operand_list) or False


@register.simple_tag
def render_sort_input(form, id_suffix) -> str:
    """
    returns sort field with name suffixed id.
    """
    bound_field = None
    for field in form:
        if field.name == "sort":
            bound_field = field
    html = ""
    if bound_field:
        html += bound_field.as_widget(
            attrs={"id": f"id_{bound_field.name}_{id_suffix}"}
        )
    return mark_safe(html)


@register.filter
def is_see_more(value) -> bool:
    """returns True if the checkbox option value is a see more"""
    if value.startswith(f"{SEE_MORE_PREFIX}{SEPERATOR}"):
        return True
    return False


@register.simple_tag()
def see_more_url(value) -> str:
    """returns the url string from checkbox option value"""
    values = value.split(SEPERATOR)
    url = values[2]  # url at index 2
    return url


@register.simple_tag(takes_context=True)
def long_filter_cancel(context, field_name: str = "") -> str:
    """Returns search url after removing long filter params"""

    request = context["request"]

    query_dict = request.GET.copy()

    if query_dict.get("group", "") == BucketKeys.COMMUNITY:
        query_dict.setlist(
            field_name,
            [
                param
                for param in query_dict.getlist(field_name, [])
                if param not in LONG_FILTER_PARAM_VALUES
            ],
        )

    return f'{reverse("search-catalogue")}?{query_dict.urlencode()}'
