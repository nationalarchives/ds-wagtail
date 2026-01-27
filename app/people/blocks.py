from app.core.blocks import (
    ContactBlock,
    InsetTextBlock,
    ParagraphBlock,
)
from wagtail import blocks


class SectionContentBlock(blocks.StreamBlock):
    contact = ContactBlock()
    inset_text = InsetTextBlock()
    paragraph = ParagraphBlock()


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"


class ResearchSummaryStreamBlock(SectionContentBlock):
    """
    A block for the GeneralPage model.
    """

    content_section = ContentSectionBlock()
