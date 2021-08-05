from django.core.paginator import Paginator
from django.http import FileResponse
from django.shortcuts import render, Http404

from ..models import Image, RecordPage
from ...ciim.exceptions import DoesNotExist, InvalidQuery


def image_viewer(request, iaid, location):
    """View to render a single image for a record."""

    try:
        page = RecordPage.search.get(iaid)
    except DoesNotExist:
        raise Http404

    if not page.is_digitised:
        raise Http404

    try:
        images = Image.search.filter(rid=page.media_reference_id)
    except InvalidQuery:
        # Raised if the RecordPage doesn't have a media_reference_id
        raise Http404

    try:
        # Find the requested image within the image set
        index, image = next(
            (index, i) for index, i in enumerate(images) if i.location == location
        )
    except StopIteration:
        # The image can't be found.
        raise Http404

    previous_image = images[max(index - 1, 0)]
    next_image = images[min(index + 1, len(images))]

    return render(
        request,
        "records/image-viewer.html",
        {
            "page": page,
            "image": image,
            "index": index,
            "next_image": next_image,
            "previous_image": previous_image,
            "location": location,
        },
    )


def image_browse(request, iaid):
    try:
        page = RecordPage.search.get(iaid)
    except DoesNotExist:
        raise Http404

    if not page.is_digitised:
        raise Http404

    try:
        images = Image.search.filter(rid=page.media_reference_id)
    except InvalidQuery:
        # Raised if the RecordPage doesn't have a media_reference_id
        raise Http404

    page_number = request.GET.get('page', 1)
    paginator = Paginator(images, 20)
    images = paginator.get_page(page_number)

    return render(
        request,
        "records/image-browse.html",
        {
            "page": page,
            "images": images,
            "paginator": paginator,
        },
    )


def image_serve(request, location):
    """Relay content served from Kong's /media endpoint"""
    response = Image.media.serve(location)

    if not response.ok:
        raise Http404

    return FileResponse(
        response.raw,
        content_type="image/jpeg",
        reason=response.reason,
    )
