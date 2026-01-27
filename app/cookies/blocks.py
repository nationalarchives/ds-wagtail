from app.core.blocks import (
    ContentTableBlock,
    DescriptionListBlock,
    InsetTextBlock,
    ParagraphBlock,
    SubHeadingBlock,
)
from wagtail import blocks


class SectionContentBlock(blocks.StreamBlock):
    inset_text = InsetTextBlock()
    paragraph = ParagraphBlock()
    description_list = DescriptionListBlock()
    sub_heading = SubHeadingBlock()
    table = ContentTableBlock()


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"


class CookieDetailsStreamBlock(SectionContentBlock):
    """
    A block for the CookieDetailsPage model.
    """

    content_section = ContentSectionBlock()
    sub_heading = None
