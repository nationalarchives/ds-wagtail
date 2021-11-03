from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import Http404, render
from django.views.decorators.cache import cache_control

from ...ciim.exceptions import DoesNotExist, InvalidQuery
from ..models import Image, RecordPage


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS, public=True)
def record_page_disambiguation_view(request, reference_number):
    """View to render a record's details page or disambiguation page if multiple records are found.

    Details pages differ from all other page types within Etna in that their
    data isn't fetched from the CMS but an external API. And unlike standrard
    Wagtail pages, this view is accessible from a fixed URL.

    Fetches by reference_number may return multiple results.

    For example ADM 223/3. This is both the catalogue reference for 1 piece and
    for the 499 item records within:

    https://discovery.nationalarchives.gov.uk/browse/r/h/C4122893
    """
    pages = RecordPage.search.filter(ref=reference_number, pretty=True)

    if len(pages) == 0:
        raise Http404

    # if the results contain a single record page, redirect to the details page.
    if len(pages) == 1:
        page = pages[0]
        return record_page_view(request, page.iaid)

    page_number = request.GET.get("page", 1)
    paginator = Paginator(pages, 20)
    pages = paginator.get_page(page_number)

    return render(
        request,
        "records/record_disambiguation_page.html",
        {
            "pages": pages,
            "queried_reference_number": reference_number,
        },
    )


@cache_control(max_age=settings.CACHE_MIDDLEWARE_SECONDS, public=True)
def record_page_view(request, iaid):
    """View for rendering a record's details page.

    Details pages differ from all other page types within Etna in that their
    data isn't fetched from the CMS but an external API. And unlike pages, this
    view is accessible from a fixed URL.
    """
    try:
        page = RecordPage.search.get(iaid, expand=True)
    except DoesNotExist:
        raise Http404

    image = None

    try:
        if page.is_digitised:
            image = Image.search.filter(rid=page.media_reference_id).first()
    except InvalidQuery:
        image = None

    return render(
        request,
        page.get_template(request),
        {
            "page": page,
            "image": image,
        },
    )
