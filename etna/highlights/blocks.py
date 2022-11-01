from wagtail.core import blocks

from etna.core.blocks import ParagraphBlock

from ..records.blocks import RecordChooserBlock


class HighlightsRecordBlock(blocks.StructBlock):
    record = RecordChooserBlock()
    date = blocks.CharBlock(
        max_length=30,
        required=False
    )
    
    class Meta:
        icon = "archive"


class CloserLookRecordBlock(blocks.StructBlock):
    record_and_date = HighlightsRecordBlock()
    paragraph = ParagraphBlock()

    class Meta:
        icon = "archive"
        