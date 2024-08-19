from wagtail import blocks

from etna.core.blocks import (
    InsetTextBlock,
    ParagraphBlock,
    QuoteBlock,
    SectionDepthAwareStructBlock,
)


class SectionContentBlock(blocks.StreamBlock):
    inset_text = InsetTextBlock()
    paragraph = ParagraphBlock()


class ContentSectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        template = "articles/blocks/section.html"


class ResearchSummaryStreamBlock(SectionContentBlock):
    """
    A block for the GeneralPage model.
    """

    content_section = ContentSectionBlock()
