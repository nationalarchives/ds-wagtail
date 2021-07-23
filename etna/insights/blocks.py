from django.conf import settings

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from ..authors.blocks import AuthorBlock
from ..paragraphs.blocks import ParagraphWithHeading
from ..quotes.blocks import QuoteBlock
from ..records.blocks import RecordChooserBlock
from ..sections.blocks import SectionBlock


class FeaturedRecordBlock(blocks.StructBlock):
    record = RecordChooserBlock()

    class Meta:
        icon = "fa-archive"
        template = "insights/blocks/featured_record.html"


class FeaturedRecordsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, required=True)
    introduction = blocks.CharBlock(max_length=200, required=True)
    records = blocks.ListBlock(
        RecordChooserBlock,
    )

    class Meta:
        icon = "fa-archive"
        template = "insights/blocks/featured_records.html"


class PromotedItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page")
    category = SnippetChooserBlock("categories.Category")
    publication_date = blocks.DateBlock()
    url = blocks.URLBlock(label="external URL", help_text="URL for the external page")
    cta_label = blocks.CharBlock(label="CTA label", max_length=50, help_text="The button label")
    teaser_image = ImageChooserBlock(
        help_text="An image used to create a teaser for the promoted page"
    )
    teaser_alt_text = blocks.CharBlock(max_length=100, help_text="Alt text of the teaser image")
    description = blocks.RichTextBlock(
        features=settings.INLINE_RICH_TEXT_FEATURES,
        help_text="A description of the promoted page"
    )

    class Meta:
        template = "insights/blocks/promoted_item.html"
        help_text = "Block used promote an external page"
        icon = "fa-star"


class InsightsPageStreamBlock(blocks.StreamBlock):
    author = AuthorBlock()
    paragraph_with_heading = ParagraphWithHeading()
    promoted_item = PromotedItemBlock()
    featured_record = FeaturedRecordBlock()
    featured_records = FeaturedRecordsBlock()
    section = SectionBlock()
