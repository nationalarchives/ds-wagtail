from wagtail import blocks

from app.core.blocks import (
    ContactBlock,
    InsetTextBlock,
    ParagraphBlock,
    PartnerLogoListBlock,
    QuoteBlock,
    SubHeadingBlock,
)


class ExhibitionPageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    quote = QuoteBlock()
    inset_text = InsetTextBlock()
    sub_heading = SubHeadingBlock()


class EventSectionContentBlock(blocks.StreamBlock):
    contact = ContactBlock()
    inset_text = InsetTextBlock()
    paragraph = ParagraphBlock()
    partner_logos = PartnerLogoListBlock()
    sub_heading = SubHeadingBlock()


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = EventSectionContentBlock(required=False)

    class Meta:
        label = "Section"


class EventPageStreamBlock(EventSectionContentBlock):
    content_section = ContentSectionBlock()
    sub_heading = None
