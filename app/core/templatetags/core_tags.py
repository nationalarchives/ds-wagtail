from django import template

register = template.Library()


@register.filter
def get(value, arg):
    """Get a value from a dictionary by key."""
    if isinstance(value, dict):
        return value.get(arg, "")
    return ""
