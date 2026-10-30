from django.core.exceptions import ValidationError
from wagtail import blocks

from app.ciim.blocks import RecordLinksBlock
from app.core.blocks import (
    AccordionsBlock,
    APIImageChooserBlock,
    APIRichTextBlock,
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


class SectionContentBlock(blocks.StreamBlock):
    accordions = AccordionsBlock()
    button = ButtonBlock()
    call_to_action = CallToActionBlock()
    code = CodeBlock()
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
    partner_logos = PartnerLogoListBlock()
    people_listing = PeopleListingBlock()
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


class ExplainerBoxBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    text = blocks.RichTextBlock(features=["bold", "link"], label="Content")

    class Meta:
        label = "Explainer Box"
        group = "Basic text"
        icon = "help"


class EasyReadSentenceBlock(blocks.StructBlock):
    image = APIImageChooserBlock()
    text = APIRichTextBlock(features=["bold", "link"], label="Content")

    class Meta:
        label = "Easy Read Sentence"
        group = "Basic text"


class EasyReadSectionContentBlock(blocks.StreamBlock):
    """
    A section content block specifically for EasyReadPage.
    """
    explainer_box = ExplainerBoxBlock()
    # featured_external_link = FeaturedExternalLinkBlock()
    # featured_page = FeaturedPageBlock() TODO: Bespoke component for CTA?
    media = MediaBlock()
    sentence = EasyReadSentenceBlock()
    sub_heading = SubHeadingBlock()
    table = ContentTableBlock()
    youtube_video = YouTubeBlock()


class EasyReadContentSectionBlock(ContentSectionBlock):
    """
    A content section block specifically for EasyReadPage.
    """
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = EasyReadSectionContentBlock()


class EasyReadStreamBlock(EasyReadSectionContentBlock):
    """
    A block for the EasyReadPage model.
    """

    content_section = EasyReadContentSectionBlock()
    sub_heading = None