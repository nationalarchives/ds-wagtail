from django.conf import settings

from wagtail.core import blocks

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


class InsightsPageStreamBlock(blocks.StreamBlock):
    author = AuthorBlock()
    paragraph_with_heading = ParagraphWithHeading()
    quote = QuoteBlock()
    featured_record = FeaturedRecordBlock()
    featured_records = FeaturedRecordsBlock()
    section = SectionBlock()
