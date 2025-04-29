from django.core.paginator import Paginator


class APIPaginator(Paginator):
    """
    Customisation of Django's Paginator class to take in the
    total number of results, number of results per page,
    and return the _count value as our total value
    """

    def __init__(self, count, per_page, **kwargs):
        self._count = int(count)
        super().__init__([], per_page, **kwargs)

    @property
    def count(self):
        return self._count
