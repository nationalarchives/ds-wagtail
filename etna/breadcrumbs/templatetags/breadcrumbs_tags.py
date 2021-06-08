from django import template

import logging

from wagtail.core.models import Page


register = template.Library()
logger = logging.getLogger(__name__)


def get_breadcrumb_items_for_page(page):
    """Fetch routable ancestors of page for display in breadcrumb."""
    return list(
        page.get_ancestors()
        # Exclude root page
        .exclude(depth=1)
        .live()
        .public()
    )


@register.inclusion_tag("breadcrumbs/tags/breadcrumbs.html", takes_context=True)
def breadcrumbs(context):
    """Output breadcrumb for given page."""
    page = context['page']

    # Return early if there's no given page e.g. on system pages like the search page.
    if not page:
        return None

    items = get_breadcrumb_items_for_page(page)

    return {
        "items": items,
        "page": page,
    }
