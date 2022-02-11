from django import forms
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property

from wagtail.core.blocks import ChooserBlock

from ..ciim.exceptions import KongAPIError, SearchManagerException


class RecordChooserBlock(ChooserBlock):
    """Custom chooser block for an externally-held record.

    Chooser adapted from the example StreamField block implementation
    documented in the wagtail-generic-chooser readme

    https://github.com/wagtail/wagtail-generic-chooser#streamfield-blocks

    With additional methods defined to handle selection of a record without a
    primary key and externally-held data.
    """

    @cached_property
    def field(self):
        """Return the associated field to pick a Record.

        ChooserBlock.field returns a ModelChoiceField. Record data is held
        externally and populated via an API call to Kong and not the database.
        """
        return forms.ChoiceField(
            choices=[],
            widget=self.widget,
            required=self._required,
            validators=self._validators,
            help_text=self._help_text,
        )

    @cached_property
    def target_model(self):
        """Defines the model used by the ChooserBlock for ID <-> instance
        conversions.
        """
        from .models import Record

        return Record

    @cached_property
    def widget(self):
        """Widget used to select a Record"""
        from .widgets import RecordChooser

        return RecordChooser()

    def get_prep_value(self, value):
        """Convert Record to IAID for persistance"""
        return value.iaid

    def bulk_to_python(self, values):
        """Return the model instances for the given list of primary keys.
        The instances must be returned in the same order as the values and keep None values.
        """
        return self.target_model.search.get_multiple(iaid=values)

    def clean(self, value):
        """Return a 'clean' value for this chooser.

        Overridden to prevent ModelChooserBlock's clean defering to
        ModelChoiceField.clean. The field checks whether the selected
        value is found within the passed queryset. Unfortunately, this
        isn't possible using externally-held data.

        Raise Validation error if form is submitted without a value.
        """
        if not value:
            raise ValidationError("Field must contain a valid record")

        return value

    def value_from_form(self, value):
        """Convert the stored IAID into a Record"""

        if not value:
            # if there's no value in the form, return None, the error will be
            # picked up in self.clean()
            return value

        try:
            return self.target_model.search.get(iaid=value)
        except (KongAPIError, SearchManagerException):
            # If there's a connection issue with Kong, return a stub Record
            # so we have something to render on the ResultsPage edit form.
            return self.target_model(iaid=value)

    def get_form_state(self, value):
        return self.widget.get_value_data(value)

    class Meta:
        icon = "archive"
