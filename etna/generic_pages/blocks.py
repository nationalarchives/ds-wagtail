from django.core.exceptions import ValidationError

from wagtail import blocks

from etna.core.blocks import (
    AccordionsBlock,
    ButtonBlock,
    CallToActionBlock,
    ContentImageBlock,
    ContentTableBlock,
    DocumentsBlock,
    DoDontListBlock,
    FeaturedRecordArticleBlock,
    ImageGalleryBlock,
    InsetTextBlock,
    ParagraphBlock,
    PromotedItemBlock,
    PromotedListBlock,
    QuoteBlock,
    SectionDepthAwareStructBlock,
    SubHeadingBlock,
    SubSubHeadingBlock,
    WarningTextBlock,
    YouTubeBlock,
)

from ..media.blocks import MediaBlock
from ..records.blocks import RecordLinksBlock


class SectionContentBlock(blocks.StreamBlock):
    accordions = AccordionsBlock()
    button = ButtonBlock()
    call_to_action = CallToActionBlock()
    document = DocumentsBlock()
    do_dont_list = DoDontListBlock()
    featured_record_article = FeaturedRecordArticleBlock()
    image = ContentImageBlock()
    image_gallery = ImageGalleryBlock()
    inset_text = InsetTextBlock()
    media = MediaBlock()
    paragraph = ParagraphBlock()
    promoted_item = PromotedItemBlock()
    promoted_list = PromotedListBlock()
    quote = QuoteBlock()
    record_links = RecordLinksBlock()
    sub_heading = SubHeadingBlock()
    sub_sub_heading = SubSubHeadingBlock()
    table = ContentTableBlock()
    warning_text = WarningTextBlock()
    youtube_video = YouTubeBlock()


class ContentSectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        template = "articles/blocks/section.html"

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
