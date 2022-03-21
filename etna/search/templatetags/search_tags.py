from dataclasses import field
from typing import Union

from django import template

register = template.Library()


@register.simple_tag
def bucket_count(api_response, bucket_name: str) -> int:
    """Output a facet count for a given bucket."""
    try:
        buckets = api_response["aggregations"]["group"]["buckets"]
    except KeyError:
        return 0

    return next(iter(a["doc_count"] for a in buckets if a["key"] == bucket_name), 0)


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


@register.simple_tag(takes_context=True)
def get_selected_filters(context) -> dict:
    """Collect selected filters from request.

    Querying the GET QueryDict instead of the form allows us to
    output a link to remove the filter even if the selected filter
    isn't returned back to us from the API.

    Returns an empty dict if no filters are selected.
    """

    request = context["request"]

    selected_filters = {
        "levels": request.GET.getlist("levels"),
        "topics": request.GET.getlist("topics"),
        "collections": request.GET.getlist("collections"),
        "closure_statuses": request.GET.getlist("closure_statuses"),
        "catalogue_sources": request.GET.getlist("catalogue_sources"),
    }

    return {k: v for k, v in selected_filters.items() if v}


@register.simple_tag(takes_context=True)
def render_hidden_form_fields(context, form: dict, *fields: str) -> str:
    """Takes a list of form fields and renders them as hidden input fields without an id tag. A field will only render if it contains a value.

    This is used instead of 'form.field.as_hidden', as this renders an id, and we need to prevent id duplication when hidden fields are reused across multiple forms on the same page.
    """
    output_html = ""
    for field_name in fields:
        field_value = form.cleaned_data.get(field_name)

        if field_value:
            if isinstance(field_value, list):
                """DynamicChoiceFields are displayed in our URLs using duplicated query string keys. For example, having two collections looks like:
                /search/catalogue?collections=collection:PROB&collections=collection:WO
                Therefore the nested_values need to be looped through and given their own hidden field.
                """
                for nested_value in field_value:
                    output_html += f"<input type='hidden' name='{field_name}' value='{nested_value}' />"
            else:
                output_html += (
                    f"<input type='hidden' name='{field_name}' value='{field_value}' />"
                )

    return output_html
