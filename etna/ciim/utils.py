import re

from django.urls import reverse

from pyquery import PyQuery as pq


def value_from_dictionary_in_list(dictionaries, key, default=None):
    return next((i for i in dictionaries if key in i), {}).get(key, default)


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
        link = pq(span).attr("link")
        if iaid := re.match(r"\$link\((?P<iaid>[C0-9]*)\)", link).group("iaid"):
            url = reverse("details-page-machine-readable", kwargs={"iaid": iaid})
            return pq(f'<a href="{url}">{pq(span).text()}</a>')

    document(".extref").each(lambda _, e: pq(e).replace_with(link_from_span(e)))

    return str(document)
