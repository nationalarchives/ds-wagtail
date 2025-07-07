from wagtail import blocks

from app.core.blocks import PageListBlock, ParagraphBlock, QuoteBlock


class WhatsOnPromotedLinksBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    promoted_links = PageListBlock(min_num=1, max_num=3)

    class Meta:
        icon = "list"


class ExhibitionPageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    quote = QuoteBlock()
