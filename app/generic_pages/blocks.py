from app.ciim.blocks import RecordLinksBlock
from app.core.blocks import (
    AccordionsBlock,
    ButtonBlock,
    CallToActionBlock,
    CodeBlock,
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
    PartnerLogoListBlock,
    PeopleListingBlock,
    QuoteBlock,
    SubHeadingBlock,
    SubSubHeadingBlock,
    WarningTextBlock,
    YouTubeBlock,
)
from app.media.blocks import MediaBlock
from django.core.exceptions import ValidationError
from wagtail import blocks


class SectionContentBlock(blocks.StreamBlock):
    accordions = AccordionsBlock(group="Structured and collapsible content")
    button = ButtonBlock(group="Onward journeys")
    call_to_action = CallToActionBlock(group="Onward journeys")
    code = CodeBlock(group="Structured and collapsible content")
    contact = ContactBlock(group="Onward journeys")
    description_list = DescriptionListBlock(group="Structured and collapsible content")
    details = DetailsBlock(group="Structured and collapsible content")
    document = DocumentsBlock(group="Video, audio and downloads")
    do_dont_list = DoDontListBlock(group="Emphasis")
    featured_external_link = FeaturedExternalLinkBlock(group="Onward journeys")
    featured_page = FeaturedPageBlock(group="Onward journeys")
    image = ContentImageBlock(group="Images")
    image_gallery = ImageGalleryBlock(group="Images")
    inset_text = InsetTextBlock(group="Emphasis")
    media = MediaBlock(group="Video, audio and downloads")
    paragraph = ParagraphBlock(group="Basic text")
    partner_logos = PartnerLogoListBlock(group="Images")
    people_listing = PeopleListingBlock(group="Onward journeys")
    quote = QuoteBlock(group="Basic text")
    record_links = RecordLinksBlock(group="Onward journeys")
    sub_heading = SubHeadingBlock(group="Basic text")
    sub_sub_heading = SubSubHeadingBlock(group="Basic text")
    table = ContentTableBlock(group="Structured and collapsible content")
    warning_text = WarningTextBlock(group="Emphasis")
    youtube_video = YouTubeBlock(group="Video, audio and downloads")


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        group = "Basic text"

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


class HubPageStreamBlock(blocks.StreamBlock):
    """
    A block for the HubPage model.
    """

    contact = ContactBlock()
    paragraph = ParagraphBlock()
    partner_logos = PartnerLogoListBlock()
