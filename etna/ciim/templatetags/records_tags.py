from django import template

register = template.Library()


# TODO: Reduce cyclomatic complexity from 14 to 12 or below
# flake8: noqa: C901
@register.simple_tag
def record_url(
    record: str,
) -> str:
    """
    TODO: This function is just a temp fix for the record_url function in the
    frontend. It'll be removed when the frontend is removed - and is only used in a few
    places so it's okay to have little logic here.
    """
    if not record:
        return ""

    return f"https://discovery.nationalarchives.gov.uk/details/r/{record}"
