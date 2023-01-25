from typing import Any

from django.core.exceptions import ValidationError
from django.db.models.fields import Field
from django.utils.functional import SimpleLazyObject

from requests import HTTPError

from .models import Record
from .widgets import RecordChooser


class LazyRecord(SimpleLazyObject):
    """
    The return type for ``RecordChooserField.from_db_value()``, which lazily
    fetches the record details from CIIM when the value is interacted
    with in some way. For example, when requesting a ``Record`` attribute
    value, like: ``obj.record.title``
    """

    def __init__(self, iaid: str):
        self.__dict__["iaid"] = iaid

        def _fetch_record():
            return Record.api.fetch(iaid=iaid)

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


class RecordChooserField(Field):
    """
    A model field that presents editors with a ``RecordChooser`` widget
    to allow selection of a record from CIIM, stores the ``iaid`` of
    that record in the database, then converts it into a ``LazyRecord``
    when the model instance is retrieved again from the database.
    """

    def __init__(self, *args, **kwargs):
        kwargs.update(max_length=50, null=True)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """
        RecordChooserFields have fixed "max_length" and "null" options,
        so we can ignore them in field breakdowns (in migrations).
        """
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["null"]
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        """
        Changes the default form field widget to a RecordChooser.
        """
        defaults = {
            "widget": RecordChooser(),
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def get_internal_type(self):
        return "CharField"

    def to_python(self, value):
        """
        Return ``None`` if the value is null or an empty string. Otherwise, use
        the "iaid" string to fetch and return a ``Record`` instance from CIIM.

        NOTE: We do not use ``LazyRecord`` here, because we want to attempt a
        record fetch as a means of validating the "iaid" value (``to_python()``
        is used in model/form validation).
        """
        if isinstance(value, str):
            try:
                return Record.api.fetch(iaid=value)
            except HTTPError:
                return ValidationError(
                    "CIIM could not return a record with iaid '{value}'. "
                )
        return value

    def from_db_value(self, value, expression, connection):
        """
        Return ``None`` if the value is null or an empty string. Otherwise,
        create and return a ``LazyRecord`` from the stored "iaid" value.
        """
        if isinstance(value, str):
            return LazyRecord(value)
        return value

    def get_prep_value(self, value):
        """
        ``None`` and string values can be used as is, but if the value is a
        ``Record`` or ``LazyRecord`` instance, extract the "iaid" value to
        store in the DB.
        """
        if isinstance(value, str):
            return value or None
        return getattr(value, "iaid", None)
