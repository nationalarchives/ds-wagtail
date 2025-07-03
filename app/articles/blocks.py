from wagtail import blocks

from app.ciim.blocks import RecordLinksBlock
from app.core.blocks import (
    ContentImageBlock,
    FeaturedExternalLinkBlock,
    FeaturedPageBlock,
    FeaturedRecordArticleBlock,
    ImageGalleryBlock,
    ParagraphBlock,
    PromotedItemBlock,
    PromotedListBlock,
    QuoteBlock,
    SectionDepthAwareStructBlock,
    SubHeadingBlock,
    YouTubeBlock,
)
from app.media.blocks import MediaBlock


class SectionContentBlock(blocks.StreamBlock):
    featured_external_link = FeaturedExternalLinkBlock()
    featured_page = FeaturedPageBlock()
    featured_record_article = FeaturedRecordArticleBlock()
    image = ContentImageBlock()
    image_gallery = ImageGalleryBlock()
    media = MediaBlock()
    paragraph = ParagraphBlock()
    promoted_item = PromotedItemBlock()
    promoted_list = PromotedListBlock()
    quote = QuoteBlock()
    record_links = RecordLinksBlock()
    sub_heading = SubHeadingBlock()
    youtube_video = YouTubeBlock()


class ContentSectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        template = "articles/blocks/section.html"


class ArticlePageStreamBlock(blocks.StreamBlock):
    content_section = ContentSectionBlock()
