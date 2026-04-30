from django.db.models import Q
from wagtail.models import Page


def skos_id_from_text(text: str) -> str:
    """
    Function to help with generation of SKOS identifiers for model instances
    that represent categories from TNA's official SKOS spec (assembled by
    Matt Hilliard).
    """
    return text.strip().replace("  ", " ").replace(" ", "_")


def get_specific_listings(
    page_types: list[Page] = [],
    filters: dict | Q = None,
    order_by: str = "start_date",
    exclude: dict = {},
    reverse: bool = False,
) -> list:
    """
    Helper function to get a list of specific pages based on the provided page
    types, filters, and order by criteria.

    This allows us to combine and compare different page types in a single
    query.
    """
    pages = []

    for page_type in page_types:
        queryset = page_type.objects.exclude(**exclude)
        if isinstance(filters, dict) or filters is None:
            queryset = queryset.filter(**(filters or {}))
        else:
            queryset = queryset.filter(filters)
        queryset = queryset.live().public().distinct()
        pages.extend(queryset)

    return sorted(pages, key=lambda page: getattr(page, order_by), reverse=reverse)
