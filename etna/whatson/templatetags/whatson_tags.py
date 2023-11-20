import re

from django import template

register = template.Library()


# Used by the event page key details bar. It strips out paragraphs and line breaks in order to display the address on one line. It also removes any links added in the rich text area, as we want to display it inside the venue url link. Other rich text formatting is preserved.
@register.filter()
def process_address(value):
    """Replaces line breaks and paragraph tags from the given string with a space. Strips out link tags."""
    value = value.replace("<br/>", " ")
    value = re.sub("<p.*?>", " ", value)
    value = value.replace("</p>", "")
    value = re.sub("<a.*?>", "", value)
    value = value.replace("</a>", "")
    return value
