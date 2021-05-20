from django.shortcuts import render

from .models import RecordPage


def record_page_view(request, catalogue_id):
    """View for rendering a record's details page.

    Details pages differ from all other page types within Etna in that their
    data isn't fetched from the CMS but an external API. And unlike pages, this
    view is accessible from a fixed URL.

    This view will eventually fetch a record from the Kong API by catalogue ID if:

     - nothing is found, 404
     - a record is found, render the page

    A RecordPage instance exists so we can map the record data to a page,
    allowing us to take advantage of the site's shared components.

    I haven't yet decided whether this object should be a concrete page type,
    or - in the spirit of Python - something that looks like a page.
    """
    page = RecordPage.search.get(catalogue_id)

    return render(
        request,
        page.get_template(request),
        {
            "page": page,
        },
    )
