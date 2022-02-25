from django import template

register = template.Library()


@register.simple_tag
def aggregation_count(kong_response, bucket_name: str) -> int:
    """This function is VERY work in progress.

    It's used to illustrate how we could parse out facet counts from an
    aggregation object.
    """
    try:
        aggregations = kong_response["aggregations"]["etna"]["buckets"]
    except KeyError:
        return 0

    return next(iter(a["doc_count"] for a in aggregations if a["key"] == bucket_name), 0)
