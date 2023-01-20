from django.db.models.fields import Field
from django.core.exceptions import ValidationError
from django.forms import ChoiceField

from ..ciim.exceptions import KongBadRequestError

from .models import Record
from .widgets import RecordChooser


class RecordChooserField(Field):
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 50
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return ChoiceField(
            choices=[],
            widget=RecordChooser(),
            required=self.blank is False,
            validators=self.validators,
            help_text=self.help_text,
            **kwargs,
        )

    def to_python(self, value):
        if isinstance(value, Record) or value is None:
            return value
        try:
            return Record.api.fetch(iaid=value)
        except KongBadRequestError as e:
            raise ValidationError(e)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return Record.api.fetch(iaid=value)

    def get_prep_value(self, value):
        if isinstance(value, Record):
            return value.iaid
        return self.to_python(value)
