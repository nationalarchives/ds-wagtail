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
