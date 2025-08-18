from django.db.models.fields import Field
from django.forms import CharField



class RecordChoiceField(CharField):
    """
    A custom Django form field that presents a record chooser widget
    by default and validates that a record can be found again from
    the selected record's ``iaid`` value.
    """

    pass

class RecordField(Field):
    """
    A model field that presents editors with a ``RecordChooser`` widget
    to allow selection of a record from CIIM, and then stores the ``iaid`` of
    that record in the database.
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
