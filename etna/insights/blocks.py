from django.conf import settings

from wagtail.core import blocks

from ..paragraphs.blocks import ParagraphWithHeading
from ..quotes.blocks import QuoteBlock
from ..records.blocks import RecordChooserBlock


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


class InsightsPageStreamBlock(blocks.StreamBlock):
    quote = QuoteBlock()
    paragraph_with_heading = ParagraphWithHeading()
    featured_record = FeaturedRecordBlock()
    featured_records = FeaturedRecordsBlock()
