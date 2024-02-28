from typing import Any

from django.core.exceptions import ValidationError
from django.db.models.fields import Field
from django.forms import CharField
from django.utils.functional import SimpleLazyObject
from requests import HTTPError

from .api import records_client
from .models import Record
from .widgets import RecordChooser


class LazyRecord(SimpleLazyObject):
    """
    The return type for ``RecordField``, which lazily fetches the
    record details from CIIM when the value is interacted with in some way;
    For example, when requesting a ``Record`` attribute value other than
    ``iaid``, or requesting a string representation of it.
    """

    def __init__(self, iaid: str):
        self.__dict__["iaid"] = iaid

        def _fetch_record():
            return records_client.fetch(iaid=iaid)

        super().__init__(_fetch_record)

    def __getattribute__(self, name: str) -> Any:
        """
        Overrides ``SimpleLazyObject.__getattribute__()`` to allow access to
        ``iaid`` without fetching the full record details from CIIM.
        """
        if name == "iaid" and "iaid" in self.__dict__:
            # The stored ``iaid`` value is not preserved when copying or
            # pickling; hence the extra conditional.
            return self.__dict__["iaid"]
        return super().__getattribute__(name)


class RecordChoiceField(CharField):
    """
    A custom Django form field that presents a record chooser widget
    by default and validates that a record can be found again from
    the selected record's ``iaid`` value.
    """

    widget = RecordChooser

    def validate(self, value: Any) -> None:
        super().validate(value)
        if value in self.empty_values:
            return None
        try:
            records_client.fetch(iaid=value)
        except HTTPError:
            raise ValidationError(
                f"Record data could not be retrieved using iaid '{value}'.",
                code="invalid",
            )


class RecordField(Field):
    """
    A model field that presents editors with a ``RecordChooser`` widget
    to allow selection of a record from CIIM, stores the ``iaid`` of
    that record in the database, then converts it into a ``LazyRecord``
    when the model instance is retrieved again from the database.
    """

    empty_values = (None, "")

    def __init__(self, *args, **kwargs):
        kwargs.update(max_length=50, null=True)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """
        RecordFields have fixed "max_length" and "null" options,
        so we can ignore them in field breakdowns (in migrations).
        """
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["null"]
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        """
        Changes the default form field to RecordChoiceField.
        """
        defaults = {
            "form_class": RecordChoiceField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def get_internal_type(self):
        return "CharField"

    @classmethod
    def _convert_to_record_instance(cls, value):
        if isinstance(value, (Record, LazyRecord)):
            return value
        if value in cls.empty_values:
            return None
        return LazyRecord(iaid=value)

    @classmethod
    def _extract_record_iaid(cls, value):
        if isinstance(value, (Record, LazyRecord)):
            return value.iaid
        if value in cls.empty_values:
            return None
        return value

    def to_python(self, value):
        """
        Return ``None`` if the value is empty. Otherwise, create and return a
        ``LazyRecord`` from the stored "iaid" value.
        """
        return self._convert_to_record_instance(value)

    def from_db_value(self, value, expression, connection):
        """
        Return ``None`` if the value is empty. Otherwise, create and return a
        ``LazyRecord`` from the stored "iaid" value.
        """
        return self._convert_to_record_instance(value)

    def get_prep_value(self, value):
        """
        If the value is a ``Record`` or ``LazyRecord`` instance, extract the
        "iaid" string to store in the DB for this field.
        """
        return self._extract_record_iaid(value)

    def value_to_string(self, model_instance):
        """
        Overrides ``Field.value_to_string`` to ensure the "iaid" string
        value is used for serialization (e.g. when converting field values
        into JSON for Wagtail revision content, or surfacing in a REST api).
        """
        value = getattr(model_instance, self.get_attname(), None)
        return self._extract_record_iaid(value)
