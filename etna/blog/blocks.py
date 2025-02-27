from wagtail import blocks

from etna.core.blocks import (
    CallToActionBlock,
    ContactBlock,
    ContentImageBlock,
    ContentTableBlock,
    DocumentsBlock,
    FeaturedExternalLinkBlock,
    FeaturedPageBlock,
    ImageGalleryBlock,
    InsetTextBlock,
    ParagraphBlock,
    QuoteBlock,
    SectionDepthAwareStructBlock,
    SubHeadingBlock,
    YouTubeBlock,
)
from etna.media.blocks import MediaBlock
from etna.records.blocks import RecordLinksBlock


class SectionContentBlock(blocks.StreamBlock):
    call_to_action = CallToActionBlock()
    contact = ContactBlock()
    document = DocumentsBlock()
    featured_external_link = FeaturedExternalLinkBlock()
    featured_page = FeaturedPageBlock()
    image = ContentImageBlock()
    image_gallery = ImageGalleryBlock()
    inset_text = InsetTextBlock()
    media = MediaBlock()
    paragraph = ParagraphBlock()
    quote = QuoteBlock()
    record_links = RecordLinksBlock()
    sub_heading = SubHeadingBlock()
    table = ContentTableBlock()
    youtube_video = YouTubeBlock()


class ContentSectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        template = "articles/blocks/section.html"


class BlogPostPageStreamBlock(SectionContentBlock):
    """
    A block for the GeneralPage model.
    """

    content_section = ContentSectionBlock()
    sub_heading = None
