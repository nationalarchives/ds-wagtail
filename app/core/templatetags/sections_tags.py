from django import template

from app.articles.blocks import ContentSectionBlock
from app.core.blocks import SectionBlock

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
