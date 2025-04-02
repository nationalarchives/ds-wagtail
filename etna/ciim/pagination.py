from django.core.paginator import Paginator


class APIPaginator(Paginator):
    """
    Customisation of Django's Paginator class for use when we don't want it to handle
    slicing on the result set, but still want it to generate the page numbering based
    on a known result count.
    """

    def __init__(self, count, per_page, **kwargs):
        self._count = int(count)
        super().__init__([], per_page, **kwargs)

    @property
    def count(self):
        return self._count

