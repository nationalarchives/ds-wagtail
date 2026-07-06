from wagtail import blocks
from wagtail.api import APIField
from wagtail.blocks import CharBlock

from app.core.blocks.image import APIImageChooserBlock

from .fields import RecordField
from .serializers import RecordSerializer


class RecordChooserBlock(CharBlock):
    """
    Custom chooser block for an externally-held record.

    Chooser adapted from the example StreamField block implementation
    from the Wagtail ChooserBlock.
    """

    def get_api_representation(self, value, context=None):
        if not value:
            return None

        serializer = RecordSerializer()
        return serializer.to_representation(value)

    def clean(self, value):
        """
        Validate the record ID using the RecordField validation logic.
        """
        field = RecordField()
        field.validate(value, None)
        return value

    class Meta:
        icon = "archive"


class RecordLinkBlock(blocks.StructBlock):
    record = RecordChooserBlock(label="Record")
    descriptive_title = blocks.CharBlock(label="Descriptive title", max_length=255)
    record_dates = blocks.CharBlock(label="Date(s)", max_length=100)
    thumbnail_image = APIImageChooserBlock(
        label="Thumbnail image (optional)", required=False
    )

    class Meta:
        icon = "archive"

    def collection(self):
        return self.record.reference_number

    api_fields = [
        APIField("collection"),
    ]


class RecordLinksBlock(blocks.StructBlock):
    items = blocks.ListBlock(RecordLinkBlock, label="Items")

    class Meta:
        icon = "box-archive"
        group = "Onward journeys"
