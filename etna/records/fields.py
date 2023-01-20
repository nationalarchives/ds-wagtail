from typing import Any

from django.core.exceptions import ValidationError
from django.db.models.fields import Field
from django.utils.functional import SimpleLazyObject

from ..ciim.exceptions import KongBadRequestError
from .models import Record
from .widgets import RecordChooser


class LazyRecord(SimpleLazyObject):
    """
    The return type for ``RecordChooserField``, which lazily fetches
    the full record details from CIIM when the value is interacted
    with in some way. For example, when requesting a ``Record``
    attribute value.
    """

    def __init__(self, iaid: str):
        self.__dict__["iaid"] = iaid

        def _do_fetch():
            try:
                return Record.api.fetch(iaid=iaid)
            except KongBadRequestError as e:
                return ValidationError(str(e))

        super().__init__(_do_fetch)

    def __getattribute__(self, name: str) -> Any:
        """
        Allow access to ``self.iaid`` without fetching the record details
        from CIIM.
        """
        if name == "iaid" and "iaid" in self.__dict__:
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
        kwargs["max_length"] = 50
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            "widget": RecordChooser(),
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def get_internal_type(self):
        return "CharField"

    def to_python(self, value):
        if isinstance(value, str):
            if not value:
                return None
            return LazyRecord(value)
        return value

    def from_db_value(self, value, expression, connection):
        if isinstance(value, str):
            if not value:
                return None
            return LazyRecord(value)
        return value

    def get_prep_value(self, value):
        if isinstance(value, str) or value is None:
            return value
        return value.iaid
