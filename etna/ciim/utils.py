import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from django.urls import reverse

from pyquery import PyQuery as pq


class MinimalResultParser:
    """
    A parser that applies a mimimal amount of tranformation to the
    dict representations from ElasticSearch, to make them a little
    more user-friendly.
    """
    def __call__(self, value):
        return_value = {}
        # Lose top-level '_source' key from ES and strip leading/trailing
        # underscores from top-level keys
        for key, v in value.get("_source", {}).items():
            return_value[key.strip('_')] = v
        # Add search match score if present
        return_value["score"] = value.get("_score")
        # Add details template values to root level for easier access
        return_value.update(return_value["template"]["details"])
        return return_value


@dataclass
class LazyResultList:
    """
    A simple wrapper-class used to represent a list of results.

    The total number of availabe results is available as `total_count`.

    The object is 'lazy', because results are stored in their original
    JSON-parsed dict representation until the object is iterated. Only then are
    results parsed using the relevant `result_parser` to make them more
    user-friendly.

    Supports slicing, len() and bool() evaluation - much like a list or tuple.
    Slicing returns a new `LazyResultList` object with an updated `results`
    value, but with all other attribute values preserved.
    """
    total_count: int
    results: List[Dict[str, Any]]
    result_parser: Callable
    aggregations: Optional[Dict[str, Any]] = None
    bucket_counts: Optional[Dict[str, int]] = None
    is_lazy: bool = True

    def __len__(self) -> int:
        return len(self.results)

    def __bool__(self):
        return bool(self.results)

    def __iter__(self):
        # Parse results if not already parsed
        self._parse_results()
        # Return parsed results one-by-one
        yield from self.results

    def __getitem__(self, key):
        if isinstance(key, int):
            result = self.results[key]
            return self.result_parser(result) if self.is_lazy else result
        sliced_results = self.results[key]
        return LazyResultList(total_count=self.total_count, results=sliced_results, result_parser=self.result_parser, aggregations=self.aggregations, bucket_counts=self.bucket_counts, is_lazy=self.is_lazy)

    def _parse_results(self):
        if not self.is_lazy:
            return
        self.results = [self.result_parser(r) for r in self.results]
        self.is_lazy = False


def pluck(collection, accessor=lambda: False, default=None):
    """Fetch a value from within a nested data structure.

    Given the list:

    "galaxies" = [{
        "name": "Milky Way",
        "planets": [{
            "name": "Jupiter",
            "moon_count": 79
        }, {
            "name": "Saturn",
            "moon_count": 82
        }]
    }]

    We're able to fetch the dict for a given planet:

    >>> pluck(planets, accessor=lambda i: i["planets"][0])
    {
        "name": "Jupiter",
        "moon_count": 79
    }

    Note that the result of the accessor function is the returned value so the
    following might be unexpected:

    >>> find(planets, accessor=lambda i: i["moon_count"] > 0)
    True

    Exceptions raised when querying the data structure are comsumed by this function.
    """
    if isinstance(collection, dict):
        collection = [collection]

    try:
        return accessor(find(collection, accessor))
    except (KeyError, IndexError, TypeError, AttributeError):
        # Catch any error that may be raised when querying data structure with
        # accessor and return fallback
        return default


def find(collection, predicate=lambda: False):
    """Find an item from a nested data structure.

    Given the list:

    planets = [{
        "name": "Jupiter",
        "moon_count": 79
    }, {
        "name": "Saturn",
        "moon_count": 82
    }]

    We're able to fetch the dict for a given planet:

    >>> find(planets, predicate=lambda i: i["name"] == "Jupiter")
    {
        "name": "Jupiter",
        "moon_count": 79
    }

    Note that only the first match is returned so predicates with multiple
    matches should be avoided or use find_all:

    >>> find(planets, predicate=lambda i: i["moon_count"] > 0)
    {
        "name": "Jupiter",
        "moon_count": 79
    }

    Exceptions raised when querying the data structure are comsumed by this function.
    """
    return next(find_all(collection, predicate), None)


def find_all(collection, predicate=lambda: False):
    """Find all items from a nested data structure.

    Given the list:

    planets = [{
        "name": "Jupiter",
        "moon_count": 79
    }, {
        "name": "Saturn",
        "moon_count": 82
    }]

    We're able to fetch the dict for a given planet:

    >>> find(planets, predicate=lambda i: i["moon_count"] > 80)
    {
        "name": "Saturn",
        "moon_count": 82
    }

    Exceptions raised when querying the data structure are comsumed by this function.
    """
    if not collection:
        collection = []

    for item in collection:
        try:
            if predicate(item):
                yield item
        except (KeyError, IndexError, TypeError, AttributeError):
            continue


def format_description_markup(markup):
    markup = resolve_links(markup)
    return markup


def strip_scope_and_content(markup):
    document = pq(markup)
    return str(document("span.scopecontent").contents().eq(0))


def resolve_links(markup):
    """Format the <span.extref> returned by CIIM into a valid HTML anchor element.

    CIIM will ultimately be responsible for URL resolution, with the added bonus that
    CIIM can check that a record is published before linking to it.

    As a stop-gap, we are replacing the <span> within Wagtail.
    """
    document = pq(markup)

    def link_from_span(span):
        if link := pq(span).attr("link"):
            if iaid := re.match(r"\$link\((?P<iaid>[C0-9]*)\)", link).group("iaid"):
                url = reverse("details-page-machine-readable", kwargs={"iaid": iaid})
                return pq(f'<a href="{url}">{pq(span).text()}</a>')
        if link := pq(span).attr("href"):
            return pq(f'<a href="{link}">{pq(span).text()}</a>')

        return ""

    document(".extref").each(lambda _, e: pq(e).replace_with(link_from_span(e)))

    return str(document)


def convert_sort_key_to_index(sort):
    """Convert key used by CIIM to sort images to pass to an ES query as an offset.

    Sort key generated by CIIM is prefixed by a number to avoid issues when
    sorting alphabetically, i.e ordering 1 , 11, 2 instead of 1, 2, 11:

    sort = "01"
    index = 0

    sort = "31000"
    index = 999

    sort = "31001"
    index = 1000
    """
    try:
        index = int(sort[1:]) - 1
    except (TypeError, ValueError):
        # Default to 0 if sort key isn't subscriptable or can't be converted to int
        index = 0

    # Ensure index is always > -1 to prevent invalid offsets being sent to Kong
    return max(index, 0)
