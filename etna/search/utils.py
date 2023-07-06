from django.conf import settings
from django.utils.text import capfirst

from wagtail.search.query import PlainText
from wagtail.search.utils import AND, normalise_query_string


def normalise_native_search_query(query: str | None) -> str | PlainText:
    # to use when searching
    if query and "AND" in query:
        logical_query_segments = []
        for segment in query.split("AND"):
            normalized = normalise_query_string(segment)
            if isinstance(normalized, str):
                logical_query_segments.append(PlainText(normalized, operator="and"))
            else:
                logical_query_segments.append(normalized)
        return AND(logical_query_segments)
    return query


def get_public_page_type_label(model):
    try:
        return capfirst(
            settings.PUBLIC_PAGE_TYPE_LABEL_OVERRIDES[model._meta.label_lower]
        )
    except (AttributeError, KeyError):
        pass

    label = capfirst(model._meta.verbose_name)
    if label.lower().endswith(" page"):
        return label[:-5]
    return label
