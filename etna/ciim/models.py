from abc import ABC

from django.conf import settings

from .client import KongClient
from .exceptions import (
    DoesNotExist,
    InvalidQuery,
    KongError,
    MultipleObjectsReturned,
    UnsupportedSlice,
)


class SearchManager:
    """A model.Manager/QuerySet-like object to query and fetch KongModel instances."""

    def __init__(self, model):
        self.model = model

    def filter(self, **kwargs):
        # Check we're making a meaningful query before contacting Kong
        if any({k: v for k, v in kwargs.items() if v is None}):
            raise InvalidQuery("Query to Kong must at least one clause")

        return SearchQuery(self.model, kwargs)

    def get(self, iaid=None, reference_number=None, expand=None):
        return FetchQuery(self.model).get(iaid=iaid, reference_number=reference_number, expand=expand)

    def get_multiple(self, iaid=None):
        return FetchQuery(self.model).get_multiple(iaid=iaid)


class ResultPending(Exception):
    """Raised if result being requested that hasn't yet been fetched."""


class ResultSet:
    """Wrapper for a list of ES search results.

    Contains a list the size of the ES results set with each item being None or
    a dict.

    If None is accessed from ResultSet, client is informed that the result
    hasn't yet been fetched from ES.
    """

    def __init__(self, total_count=0):
        self.results = [None] * total_count

    def __getitem__(self, index):
        """Support subscripting.

        Raise IndexError if requested item is not in list
        or ResultPending if item hasn't been fetched yet.
        """
        result = self.results[index]
        if not result:
            raise ResultPending

        return result

    def add(self, results, start=0):
        """Add a list of results at a specified point."""
        for index, result in zip(range(start, start + len(results)), results):
            self.results[index] = result


class Query(ABC):
    """Abstract base class to inherit from to create a Query"""

    @property
    def client(self):
        """Lazy-load client to allow tests to overwrite base url."""
        return KongClient(
            settings.KONG_CLIENT_BASE_URL,
            api_key=settings.KONG_CLIENT_KEY,
            verify_certificates=settings.KONG_CLIENT_VERIFY_CERTIFICATES,
        )


class SearchQuery(Query):
    """Support queries to Kong's /search method.

    Once configured via SearchManager.filter, this class is responsible for
    fetching and transforming responses into model instances.
    """

    BATCH_SIZE = 10

    def __init__(self, model, query):
        self.model = model
        self._response = {}
        self._results = []
        self._query = query

    def _fetch(self, start=0, size=1):
        """Fetch and update ResultSet"""
        self._response = self.client.search(start=start, size=size, **self._query)

        if not self._results:
            self._results = ResultSet(
                total_count=self._response["hits"]["total"]["value"]
            )

        if hits := self._response["hits"]["hits"]:
            self._results.add(hits, start)

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
        is_single_item_fetch = key.start is not None and not key.stop

        if is_single_item_fetch:
            try:
                result = self._results[key.start]
            except (ResultPending, IndexError):
                self._fetch(start=key.start, size=self.BATCH_SIZE)
                result = self._results[key.start]

            transformed_result = self.model.transform(result)
            return self.model(**transformed_result)

        self._fetch(start=key.start, size=count)
        translated_results = [self.model.transform(r) for r in self._results[key]]
        return [self.model(**r) for r in translated_results]

    def __len__(self):
        """Support len()"""
        return self.count()

    def count(self):
        self._fetch(start=0, size=0)
        return self._response["hits"]["total"]["value"]

    def first(self):
        """Return the first item in resultset without or None if nothing is found."""
        try:
            return self[0]
        except IndexError:
            return None


class FetchQuery(Query):
    """Support queries to Kong's /fetch method.

    Once configured via SearchManager.get, this class is responsible for
    fetching and transforming responses into model instances.
    """

    def __init__(self, model):
        self.model = model

    def get(self, iaid=None, reference_number=None, expand=False):
        response = self.client.fetch(iaid=iaid, reference_number=reference_number, expand=expand)

        results = response["hits"]["hits"]
        results_count = response["hits"]["total"]["value"]
        if results_count == 0:
            raise DoesNotExist
        if results_count > 1:
            raise MultipleObjectsReturned

        result = results[0]

        data = self.model.transform(result)
        data["_debug_kong_result"] = result

        return self.model(**data)

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


class MediaQuery(Query):
    """Support queries to Kong's /media method."""

    def __init__(self, model):
        self.model = model

    def serve(self, location):
        return self.client.media(location=location)


class MediaManager:
    """A model.Manager/QuerySet-like object to serve images though Kong's media service."""

    def __init__(self, model):
        self.model = model

    def serve(self, location):
        return MediaQuery(self.model).serve(location=location)
