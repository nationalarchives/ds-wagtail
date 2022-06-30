import json

from json.decoder import JSONDecodeError
from urllib.parse import unquote

from django import template

from etna.core.blocks import SectionBlock
from etna.insights.blocks import ContentSectionBlock

register = template.Library()


@register.inclusion_tag("includes/jumplinks.html")
def jumplinks(page):
    sections = []
    for boundblock in page.body:
        if isinstance(boundblock.block, (SectionBlock, ContentSectionBlock)):
            sections.append(
                {
                    "heading_text": boundblock.value["heading"],
                    "heading_id": boundblock.block.get_heading_id(boundblock.value),
                }
            )
    return {
        "sections": sections,
    }


@register.filter
def cookie_usage(record: dict) -> bool:
    """
    Return the True/False based on cookie usage value
    if no cookie set it will return False
    """
    try:
        usage = False
        if "cookies_policy" in record:
            cookie_str = unquote(record["cookies_policy"])
            # Use Record property if available
            usage = json.loads(cookie_str)["usage"]
    except JSONDecodeError:
        usage = False
    return usage
