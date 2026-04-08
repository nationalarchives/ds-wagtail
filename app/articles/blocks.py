from app.ciim.blocks import RecordLinksBlock
from app.core.blocks import (
    CodeBlock,
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
from wagtail import blocks


class SectionContentBlock(blocks.StreamBlock):
    code = CodeBlock(group="Structured and collapsible content")
    featured_external_link = FeaturedExternalLinkBlock(group="Onward journeys")
    featured_page = FeaturedPageBlock(group="Onward journeys")
    image = ContentImageBlock(group="Images")
    image_gallery = ImageGalleryBlock(group="Images")
    media = MediaBlock(group="Video, audio and downloads")
    paragraph = ParagraphBlock(group="Basic text")
    quote = QuoteBlock(group="Basic text")
    record_links = RecordLinksBlock(group="Onward journeys")
    sub_heading = SubHeadingBlock(group="Basic text")
    youtube_video = YouTubeBlock(group="Video, audio and downloads")


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"


class ArticlePageStreamBlock(blocks.StreamBlock):
    content_section = ContentSectionBlock()
