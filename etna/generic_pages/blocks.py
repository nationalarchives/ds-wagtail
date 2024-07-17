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
    InsetTextBlock,
    ParagraphBlock,
    PromotedItemBlock,
    PromotedListBlock,
    QuoteBlock,
    SectionDepthAwareStructBlock,
    SubHeadingBlock,
    WarningTextBlock,
    YouTubeBlock,
)

from ..media.blocks import MediaBlock
from ..records.blocks import RecordLinksBlock


class SectionContentBlock(blocks.StreamBlock):
    accordion = AccordionsBlock()
    button = ButtonBlock()
    call_to_action = CallToActionBlock()
    document = DocumentsBlock()
    do_dont_list = DoDontListBlock()
    featured_record_article = FeaturedRecordArticleBlock()
    image = ContentImageBlock()
    inset_text = InsetTextBlock()
    media = MediaBlock()
    paragraph = ParagraphBlock()
    promoted_item = PromotedItemBlock()
    promoted_list = PromotedListBlock()
    quote = QuoteBlock()
    record_links = RecordLinksBlock()
    sub_heading = SubHeadingBlock()
    table = ContentTableBlock()
    warning_text = WarningTextBlock()
    youtube_video = YouTubeBlock()


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
