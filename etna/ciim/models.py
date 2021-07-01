from django.apps import apps
from django.conf import settings

from .client import KongClient
from .exceptions import (
    DoesNotExist,
    MultipleObjectsReturned,
    KongError,
    UnsupportedSlice,
)
from .utils import translate_result


class ResultsIterator:
    def __init__(self, model, results):
        self.model = model
        self.results = results
        self.index = 0

    def __next__(self):
        try:
            result = self.results[self.index]
        except IndexError:
            raise StopIteration

        self.index += 1

        translated_result = translate_result(result)
        return apps.get_model(self.model)(**translated_result)


class SearchManager:
    """A model.Manager/QuerySet-like object to query and fetch KongModel instances."""

    def __init__(self, model):
        self.model = model
        self._response = {}
        self._results = []
        self._query = {}
        self._cache = {}

    @property
    def client(self):
        """Lazy-load client to allow tests to overwrite base url."""
        return KongClient(settings.KONG_CLIENT_BASE_URL)

    def filter(self, **kwargs):
        self._query = kwargs

        return self

    def get(self, iaid=None, reference_number=None):
        response = self.client.fetch(iaid=iaid, reference_number=reference_number)

        results = response["hits"]["hits"]
        results_count = response["hits"]["total"]["value"]
        if results_count == 0:
            raise DoesNotExist
        if results_count > 1:
            raise MultipleObjectsReturned

        result = results[0]

        data = translate_result(result)

        return apps.get_model(self.model)(**data)

    def get_multiple(self, iaid=None):
        """Temporary method created to fetch multiple items.

        Currently uses multiple calls to SearchManager.get. Not suitable
        for production code"""
        ids = iaid or []

        records = []

        for iaid in ids:
            try:
                instance = self.get(iaid=iaid)
            except (KongError, DoesNotExist):
                continue
            records.append(instance)

        return records

    def _fetch(self):
        self._response = self.client.search(**self._query)
        self._results = self._response["hits"]["hits"]

    def __getitem__(self, key):
        """Support subscripts to allow results set to be paginated.

        Due to the complexity of paging through an API response, the following
        aren't supported and will raise an UnsupportedSlice error:

        - Negative keys to access results from the end of result set [-1]
        - Fetching all results [:]
        - Fetches with a step [0:1:2]

        https://docs.python.org/3/reference/datamodel.html#object.__getitem__
        """

        if key == slice(None, None, None):
            raise UnsupportedSlice(
                "Slicing to return all records ([:]) is not supported"
            )

        # Key can be an int (in the case of positional fetches [0]) or a slice.
        # Convert int to slice to make comparisons easier.
        if isinstance(key, int):
            key = slice(key, None, None)

        if key.step:
            raise UnsupportedSlice("Slicing with step is not supported")

        if key.start < 0:
            raise UnsupportedSlice("Slicing with negative index not supported")

        start = key.start
        stop = key.stop or 0

        count = max(1, stop - start)

        self._query["start"] = start
        self._query["size"] = count

        self._fetch()

        # If positional fetch, return single item, otherwise return all fetched results.
        if key.start is not None and not key.stop:
            translated_result = translate_result(self._results[key.start])
            return apps.get_model(self.model)(**translated_result)
        else:
            translated_results = [translate_result(r) for r in self._results]
            return [apps.get_model(self.model)(**r) for r in translated_results]

    def __len__(self):
        """Support len()"""
        return self.count()

    def count(self):
        self._fetch()
        return self._response["hits"]["total"]["value"]

    def __iter__(self):
        self._fetch()
        return ResultsIterator(self.model, self._results)
