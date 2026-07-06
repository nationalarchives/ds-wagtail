import re

from django.core.exceptions import ValidationError
from django.db.models import CharField


class RecordField(CharField):
    """
    A model field that presents editors with a ``RecordChooser`` widget
    to allow selection of a record from CIIM, and then stores the ``iaid`` of
    that record in the database.
    """

    RECORD_ID_PATTERN = re.compile(
        r"^(?:"
        r"[0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{12}"
        r"|"
        r"[A-Z][0-9]+"
        r")$"
    )

    def __init__(self, *args, **kwargs):
        kwargs.update(max_length=50, null=True)
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        if value and not self.RECORD_ID_PATTERN.fullmatch(value):
            raise ValidationError("Enter a valid record ID")

        return super().validate(value, model_instance)
