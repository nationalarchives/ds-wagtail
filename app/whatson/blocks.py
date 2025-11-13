from wagtail import blocks

from app.core.blocks import (
    ContactBlock,
    InsetTextBlock,
    ParagraphBlock,
    QuoteBlock,
    SubHeadingBlock,
)


class ExhibitionPageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    quote = QuoteBlock()
    inset_text = InsetTextBlock()
    sub_heading = SubHeadingBlock()


class SectionContentBlock(blocks.StreamBlock):
    contact = ContactBlock()
    inset_text = InsetTextBlock()
    paragraph = ParagraphBlock()
    sub_heading = SubHeadingBlock()


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"


class EventPageStreamBlock(SectionContentBlock):
    content_section = ContentSectionBlock()
    sub_heading = None
