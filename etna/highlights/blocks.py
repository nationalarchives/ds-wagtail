from wagtail.core import blocks

from etna.core.blocks import ParagraphBlock

from ..records.blocks import RecordChooserBlock


class HighlightsRecordBlock(blocks.StructBlock):
    record = RecordChooserBlock()
    date = blocks.CharBlock(max_length=30, required=False)
    paragraph = ParagraphBlock()

    class Meta:
        icon = "archive"
