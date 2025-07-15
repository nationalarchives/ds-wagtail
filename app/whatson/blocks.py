from wagtail import blocks

from app.core.blocks import (
    ContactBlock,
    InsetTextBlock,
    PageListBlock,
    ParagraphBlock,
    QuoteBlock,
    SectionDepthAwareStructBlock,
    SubHeadingBlock,
)


class WhatsOnPromotedLinksBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    promoted_links = PageListBlock(min_num=1, max_num=3)

    class Meta:
        icon = "list"


class ExhibitionPageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    quote = QuoteBlock()


class SectionContentBlock(blocks.StreamBlock):
    contact = ContactBlock()
    inset_text = InsetTextBlock()
    paragraph = ParagraphBlock()
    sub_heading = SubHeadingBlock()


class ContentSectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        template = "articles/blocks/section.html"


class EventPageStreamBlock(SectionContentBlock):
    content_section = ContentSectionBlock()
    sub_heading = None
