from app.ciim.blocks import RecordLinksBlock
from app.core.blocks import (
    CallToActionBlock,
    CodeBlock,
    ContactBlock,
    ContentImageBlock,
    ContentTableBlock,
    DocumentsBlock,
    FeaturedExternalLinkBlock,
    FeaturedPageBlock,
    ImageGalleryBlock,
    InsetTextBlock,
    ParagraphBlock,
    PartnerLogoListBlock,
    QuoteBlock,
    SubHeadingBlock,
    YouTubeBlock,
)
from app.media.blocks import MediaBlock
from wagtail import blocks


class SectionContentBlock(blocks.StreamBlock):
    call_to_action = CallToActionBlock(group="Onward journeys")
    code = CodeBlock(group="Structured and collapsible content")
    contact = ContactBlock(group="Onward journeys")
    document = DocumentsBlock(group="Video, audio and downloads")
    featured_external_link = FeaturedExternalLinkBlock(group="Onward journeys")
    featured_page = FeaturedPageBlock(group="Onward journeys")
    image = ContentImageBlock(group="Images")
    image_gallery = ImageGalleryBlock(group="Images")
    inset_text = InsetTextBlock(group="Emphasis")
    media = MediaBlock(group="Video, audio and downloads")
    paragraph = ParagraphBlock(group="Basic text")
    partner_logos = PartnerLogoListBlock(group="Images")
    quote = QuoteBlock(group="Basic text")
    record_links = RecordLinksBlock(group="Onward journeys")
    sub_heading = SubHeadingBlock(group="Basic text")
    table = ContentTableBlock(group="Structured and collapsible content")
    youtube_video = YouTubeBlock(group="Video, audio and downloads")


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        group = "Basic text"


class BlogPostPageStreamBlock(SectionContentBlock):
    """
    A block for the GeneralPage model.
    """

    content_section = ContentSectionBlock()
    sub_heading = None
