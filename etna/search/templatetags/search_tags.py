from django import template
from django.http import QueryDict

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
def record_title(record) -> str:
    """Output a record's title.

    Django templates don't allow access to keys or attributes prefixed with _

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """
    try:
        return record["_source"]["@template"]["details"]["summaryTitle"]
    except KeyError:
        return "No Title Found"


@register.filter
def record_iaid(record) -> str:
    """Output a record's iaid.

    Django templates don't allow access to keys or attributes prefixed with _

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """
    try:
        return record["_source"]["@template"]["details"]["iaid"]
    except KeyError:
        return "No IAID Found"


@register.filter
def record_score(record) -> str:
    """Output a record's score.

    Django templates don't allow access to keys or attributes prefixed with _

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """
    return record.get("_score")


@register.simple_tag(takes_context=True)
def query_string(context, **kwargs) -> str:
    """Update  query string for context's request with passed kwargs."""

    request = context["request"]

    query_dict = QueryDict(mutable=True)
    query_dict.update(request.GET)

    for k, v in kwargs.items():
        query_dict[k] = v

    return query_dict.urlencode()
