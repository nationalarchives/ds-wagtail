from django import template

from ..blocks import SectionBlock

register = template.Library()


@register.inclusion_tag("sections/tags/jumplinks.html")
def jumplinks(page):
    return {
        "sections": [
            block.value for block in page.body if isinstance(block.block, SectionBlock)
        ]
    }
