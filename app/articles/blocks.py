from wagtail import blocks

from app.ciim.blocks import RecordLinksBlock
from app.core.blocks import (
    ContentImageBlock,
    FeaturedExternalLinkBlock,
    FeaturedPageBlock,
    ImageGalleryBlock,
    ParagraphBlock,
    QuoteBlock,
    SubHeadingBlock,
    YouTubeBlock,
)
from app.media.blocks import MediaBlock


class SectionContentBlock(blocks.StreamBlock):
    featured_external_link = FeaturedExternalLinkBlock()
    featured_page = FeaturedPageBlock()
    image = ContentImageBlock()
    image_gallery = ImageGalleryBlock()
    media = MediaBlock()
    paragraph = ParagraphBlock()
    quote = QuoteBlock()
    record_links = RecordLinksBlock()
    sub_heading = SubHeadingBlock()
    youtube_video = YouTubeBlock()


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"


class ArticlePageStreamBlock(blocks.StreamBlock):
    content_section = ContentSectionBlock()
