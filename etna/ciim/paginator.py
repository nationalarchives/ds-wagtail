from django.core.paginator import Paginator


class APIPaginator(Paginator):
    """
    Custom paginator to page through API responses.

    Paginator requires API request to be made before passing the results count
    when instantiating the Paginator.

    Taken from wagtail-generic-chooser.

    https://github.com/wagtail/wagtail-generic-chooser/blob/6d21c64d2f0e3ab6342def4548785c93df9be2db/generic_chooser/views.py#L551-L567
    """

    def __init__(self, count, per_page, **kwargs):
        self._count = int(count)
        super().__init__([], per_page, **kwargs)

    @property
    def count(self):
        return self._count
