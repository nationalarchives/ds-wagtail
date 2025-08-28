from django.db.models import CharField


class RecordField(CharField):
    """
    A model field that presents editors with a ``RecordChooser`` widget
    to allow selection of a record from CIIM, and then stores the ``iaid`` of
    that record in the database.
    """

    def __init__(self, *args, **kwargs):
        kwargs.update(max_length=50, null=True)
        super().__init__(*args, **kwargs)
