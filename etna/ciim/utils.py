import re
from typing import Any, Dict, Optional

import nh3
from django.urls import NoReverseMatch, reverse
from pyquery import PyQuery as pq


def underscore_to_camelcase(word, lower_first=True):
    result = "".join(char.capitalize() for char in word.split("_"))
    if lower_first:
        result = result[0].lower() + result[1:]
    return result


class ValueExtractionError(Exception):
    pass


NOT_PROVIDED = "__np__"


def extract(
    source: Dict[str, Any], key: str, default: Optional[Any] = NOT_PROVIDED
) -> Any:
    """
    Attempts to extract `key` (a string with multiple '.' to indicate
    traversal) from `source` (a complex multi-level dict where values may
    by lists or other complex types) and return the value.

    If `default` is provided, that value will be returned if any issues
    arise during the process. When no `default` is provied, a
    `ValueExtractionError` is raised instead.
    """
    current = source
    lookups = tuple(key.split("."))

    try:
        for bit in lookups:
            # NOTE: we could use a series of nested try/excepts here instead,
            # but using conditionals allows us to raise more relevant exceptions

            # Only attempt key lookups for dicts
            if isinstance(current, dict):
                current = current[bit]
                continue

            # Only attempt index lookups for sequences, and only
            # when the value looks like an index
            if hasattr(current, "__getitem__"):
                try:
                    bit_index = int(bit)
                except ValueError:
                    pass
                else:
                    current = current[bit_index]  # do index lookup
                    continue

            # Always fall back to attribute lookup
            current = getattr(current, bit)

    except Exception as e:
        if default is NOT_PROVIDED:
            raise ValueExtractionError(
                f"'{key}' could not be extracted. {type(e)} raised when extracting '{bit}' from {current}."
            )
        return default

    return current


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
    return resolve_links(markup)


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

    # Ensure index is always > -1 to prevent invalid offsets being sent to Client API
    return max(index, 0)


def format_link(link_html: str) -> Dict[str, str]:
    """
    Extracts iaid and text from a link HTML string, e.g. "<a href="C5789">DEFE 31</a>"
    and returns as dict in the format: `{"id":"C5789", "href": "/catalogue/id/C5789/", "text":"DEFE 31"}
    """
    document = pq(link_html)
    id = document.attr("href")
    try:
        href = reverse("details-page-machine-readable", kwargs={"iaid": id})
    except NoReverseMatch:
        href = ""
    return {"href": href, "id": id, "text": document.text()}


def strip_html(
    value: str,
    *,
    preserve_marks: bool = False,
    ensure_spaces: bool = False,
    allow_tags: Optional[set] = None,
) -> str:
    """
    Temporary HTML sanitiser to remove unwanted tags from data.
    TODO:this will eventually be sanitised at API level.

    value:
        the value to be sanitised
    preserver_marks:
        allow pre-defined tags for styling
    ensure_spaces:
        allow pre-defined tags and replaces them with whitespace
    allow_tags:
        sets the tags that are allowed
    """
    clean_tags = {"span", "p"} if ensure_spaces else set()

    if allow_tags is None:
        allow_tags = set()

    tags = set()
    if preserve_marks:
        tags.add("mark")
    tags.update(clean_tags)
    tags.update(allow_tags)

    clean_html = nh3.clean(value, tags=tags)

    for tag in clean_tags:
        opening_regex = rf"<{tag}[^>]*>"
        closing_regex = rf"</{tag}>"
        clean_html = re.sub(opening_regex, " ", clean_html)
        clean_html = re.sub(closing_regex, "", clean_html)
    return clean_html.lstrip()
