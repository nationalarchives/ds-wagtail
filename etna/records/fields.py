from typing import Any

from django.core.exceptions import ValidationError
from django.db.models.fields import Field
from django.forms import CharField
from django.utils.functional import SimpleLazyObject
from requests import HTTPError

from etna.ciim.exceptions import DoesNotExist

from .api import records_client
from .models import Record
from .widgets import RecordChooser
from .views.choosers import BaseRecordChooserWidget


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
            try:
                return records_client.fetch(iaid=iaid)
            except DoesNotExist:
                return None

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

    widget = BaseRecordChooserWidget


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
