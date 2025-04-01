from django.forms.fields import Field
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.api import APIField

from etna.ciim.exceptions import ClientAPIError
from etna.core.blocks.image import APIImageChooserBlock

from .api import records_client
from .fields import RecordChoiceField
from .views.choosers import BaseRecordChooserWidget
from wagtail.blocks.field_block import FieldBlock
import requests
from django.conf import settings


class RecordChooserBlock(FieldBlock):
    """
    Custom chooser block for an externally-held record.

    Chooser adapted from the example StreamField block implementation
    from the Wagtail ChooserBlock.
    """
    def __init__(self, help_text=None, **kwargs):
        self.field = RecordChoiceField(help_text=help_text)
        super().__init__(**kwargs)

    def value_for_form(self, value):
        """
        Reverse of value_from_form; convert a value of this block's native value type
        to one that can be rendered by the form field
        """
        if not value:
            # if there's no value in the form, return None
            return value
        r = requests.get(f"{settings.CLIENT_BASE_URL}/get?id={value}")
        result = r.json()
        result = result.get("data", [])[0].get("@template", {}).get("details", {})
        print({
            "id": result.get("iaid"),
            "title": f"{result["summaryTitle"]} ({result["iaid"]})",
        })
        return {
            "id": result.get("iaid"),
            "title": f"{result["summaryTitle"]} ({result["iaid"]})",
        }
    
    def value_from_form(self, value):
        return value
    
    class Meta:
        icon = "archive"

# class RecordChooserBlock(blocks.ChooserBlock):
#     """Custom chooser block for an externally-held record.

#     Chooser adapted from the example StreamField block implementation
#     documented in the wagtail-generic-chooser readme

#     https://github.com/wagtail/wagtail-generic-chooser#streamfield-blocks

#     With additional methods defined to handle selection of a record without a
#     primary key and externally-held data.
#     """

#     @cached_property
#     def field(self):
#         """Return the associated field to pick a Record.

#         ChooserBlock.field returns a ModelChoiceField. Record data is held
#         externally and populated via an API call to Client API and not the database.
#         """
#         return forms.ChoiceField(
#             choices=[],
#             widget=self.widget,
#             required=self._required,
#             validators=self._validators,
#             help_text=self._help_text,
#         )

#     def get_prep_value(self, value):
#         """Convert Record to IAID for persistance"""
#         return value

#     # def bulk_to_python(self, values):
#     #     """Return a list of model instances for the given list of primary keys.
#     #     The instances must be returned in the same order as the values and keep None values.
#     #     """
#     #     if not values:
#     #         return []
#     #     records_by_id = {r.iaid: r for r in records_client.fetch_all(iaids=values)}
#     #     return list(records_by_id.get(iaid) for iaid in values)

#     def clean(self, value):
#         """Return a 'clean' value for this chooser.

#         Overridden to prevent ModelChooserBlock's clean defering to
#         ModelChoiceField.clean. The field checks whether the selected
#         value is found within the passed queryset. Unfortunately, this
#         isn't possible using externally-held data.

#         Raise Validation error if form is submitted without a value.
#         """
#         if not value:
#             raise ValidationError("Field must contain a valid record")

#         return value

#     # def value_from_form(self, value):
#     #     """Convert the stored IAID into a Record"""

#     #     if not value:
#     #         # if there's no value in the form, return None, the error will be
#     #         # picked up in self.clean()
#     #         return value

#     #     try:
#     #         return records_client.fetch(iaid=value)
#     #     except ClientAPIError:
#     #         # If there's a connection issue with Client API, return a stub Record
#     #         # so we have something to render on the ResultsPage edit form.
#     #         return self.target_model(raw_data={"iaid": value})

#     # def get_form_state(self, value):
#     #     return self.widget.get_value_data(value)

#     # def extract_references(self, value):
#     #     """This overrides the extract_references function from ChooserBlock to prevent
#     #     Wagtail's reference index from rebuilding this block"""
#     #     return []

#     def get_api_representation(self, value, context=None):
#         if value:
#             return {
#                 "title": value.summary_title,
#                 "iaid": value.iaid,
#                 "reference_number": value.reference_number,
#             }
#         return None

#     class Meta:
#         icon = "archive"


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
