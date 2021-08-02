import re

from django.urls import reverse

from pyquery import PyQuery as pq


def translate_result(result):
    data = {}

    source = result["_source"]
    identifier = source.get("identifier")
    summary = source.get("@summary")

    data["iaid"] = source["@admin"]["id"]
    data["reference_number"] = pluck(
        identifier, accessor=lambda i: i.get("reference_number")
    )
    data["title"] = summary.get("title")

    if access := source.get("access"):
        data["closure_status"] = access.get("conditions")

    if origination := source.get("@origination"):
        data["created_by"] = pluck(
            origination, accessor=lambda i: i["creator"][0]["name"][0]["value"]
        )
        if origination["date"]["value"] != "undated":
            data["date_start"] = origination["date"]["earliest"]["from"]
            data["date_end"] = origination["date"]["latest"]["to"]
            data["date_range"] = origination["date"]["value"]

    if description := source.get("description"):
        data["description"] = format_description_markup(description[0]["value"])

    if arrangement := source.get("arrangement"):
        data["arrangement"] = format_description_markup(arrangement["value"])

    if legal := source.get("legal"):
        data["legal_status"] = legal["status"]

    if repository := source.get("repository"):
        data["held_by"] = repository["name"]["value"]

    data["is_digitised"] = source.get("digitised", False)

    if parent := find(
        source.get("association"),
        predicate=lambda i: i["@link"]["role"][0]["value"] == "parent",
    ):
        data["parent"] = {
            "iaid": parent["@admin"]["id"],
            "title": parent["@summary"]["title"],
        }

    if hierarchy := source.get("hierarchy"):
        data["hierarchy"] = [
            {
                "reference_number": i["identifier"][0]["reference_number"],
                "title": i["@summary"]["title"],
            }
            # The last record in the hierarchy is the current record.
            # Exclude from parsed data
            for i in hierarchy[0][:-1]
        ]

    return data


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
    matches should be avoided:

    >>> find(planets, predicate=lambda i: i["moon_count"] > 0)
    {
        "name": "Jupiter",
        "moon_count": 79
    }

    Exceptions raised when querying the data structure are comsumed by this function.
    """
    try:
        return next(filter(predicate, collection), None)
    except (KeyError, IndexError, TypeError, AttributeError):
        # Catch any error that may be raised when querying data structure with
        # predicate and return fallback
        return None


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

    document(".extref").each(lambda _, e: pq(e).replace_with(link_from_span(e)))

    return str(document)
