from django import template

register = template.Library()


@register.filter()
def is_search_or_catalogue(path) -> bool:
    """Return True if path is contained in search or catalogue."""
    return path.startswith("/search/") or path.startswith("/catalogue/")
