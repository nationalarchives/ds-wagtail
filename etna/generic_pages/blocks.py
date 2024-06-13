from wagtail import blocks

from etna.core.blocks import ParagraphBlock


from wagtail import blocks

from etna.core.blocks import (
    ContentImageBlock,
    FeaturedRecordArticleBlock,
    ParagraphBlock,
    PromotedListBlock,
    PromotedItemBlock,
    QuoteBlock,
    SubHeadingBlock,
    SectionDepthAwareStructBlock
)
from ..media.blocks import MediaBlock
from ..records.blocks import RecordLinksBlock


class SectionContentBlock(blocks.StreamBlock):
    featured_record_article = FeaturedRecordArticleBlock()
    image = ContentImageBlock()
    media = MediaBlock()
    paragraph = ParagraphBlock()
    promoted_item = PromotedItemBlock()
    promoted_list = PromotedListBlock()
    quote = QuoteBlock()
    record_links = RecordLinksBlock()
    sub_heading = SubHeadingBlock()


class ContentSectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        template = "articles/blocks/section.html"


class GeneralPageStreamBlock(blocks.StreamBlock):
    """
    A block for the GeneralPage model.
    """
    content_section = ContentSectionBlock()
