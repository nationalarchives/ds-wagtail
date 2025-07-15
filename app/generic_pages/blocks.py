from django.core.exceptions import ValidationError
from wagtail import blocks

from app.ciim.blocks import RecordLinksBlock
from app.core.blocks import (
    AccordionsBlock,
    ButtonBlock,
    CallToActionBlock,
    ContactBlock,
    ContentImageBlock,
    ContentTableBlock,
    DescriptionListBlock,
    DetailsBlock,
    DocumentsBlock,
    DoDontListBlock,
    FeaturedExternalLinkBlock,
    FeaturedPageBlock,
    ImageGalleryBlock,
    InsetTextBlock,
    ParagraphBlock,
    QuoteBlock,
    SubHeadingBlock,
    SubSubHeadingBlock,
    WarningTextBlock,
    YouTubeBlock,
)
from app.media.blocks import MediaBlock


class SectionContentBlock(blocks.StreamBlock):
    accordions = AccordionsBlock()
    button = ButtonBlock()
    call_to_action = CallToActionBlock()
    contact = ContactBlock()
    description_list = DescriptionListBlock()
    details = DetailsBlock()
    document = DocumentsBlock()
    do_dont_list = DoDontListBlock()
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
    sub_sub_heading = SubSubHeadingBlock()
    table = ContentTableBlock()
    warning_text = WarningTextBlock()
    youtube_video = YouTubeBlock()


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"

    def clean(self, value):
        clean = super().clean(value)
        has_sub_heading = False
        content = clean.get("content")

        for block in content:
            block_type = block.block_type
            if block_type == "sub_heading":
                has_sub_heading = True
            elif block_type == "sub_sub_heading" and not has_sub_heading:
                raise ValidationError(
                    "A sub-sub-heading was found before any sub-headings."
                )
        return clean


class GeneralPageStreamBlock(SectionContentBlock):
    """
    A block for the GeneralPage model.
    """

    content_section = ContentSectionBlock()
    sub_heading = None
    sub_sub_heading = None
