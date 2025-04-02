from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.api import APIField

from etna.core.blocks.image import APIImageChooserBlock

from .fields import RecordChoiceField
from .views.choosers import BaseRecordChooserWidget
from wagtail.blocks.field_block import FieldBlock

class RecordChooserBlock(FieldBlock):
    """
    Custom chooser block for an externally-held record.

    Chooser adapted from the example StreamField block implementation
    from the Wagtail ChooserBlock.
    """

    widget = BaseRecordChooserWidget()

    def __init__(self, help_text=None, **kwargs):
        self.field = RecordChoiceField(help_text=help_text)
        super().__init__(**kwargs)

    def get_form_state(self, value):
        return self.widget.get_value_data(value)

    class Meta:
        icon = "archive"


class RecordLinkBlock(blocks.StructBlock):
    record = RecordChooserBlock(label=_("Record"))
    descriptive_title = blocks.CharBlock(label=_("Descriptive title"), max_length=255)
    record_dates = blocks.CharBlock(label=_("Date(s)"), max_length=100)
    thumbnail_image = APIImageChooserBlock(
        label=_("Thumbnail image (optional)"), required=False
    )

    class Meta:
        icon = "archive"

    def collection(self):
        return self.record.reference_number

    api_fields = [
        APIField("collection"),
    ]


class RecordLinksBlock(blocks.StructBlock):
    items = blocks.ListBlock(RecordLinkBlock, label=_("Items"))

    class Meta:
        template = "records/blocks/record_links_block.html"
        icon = "box-archive"
