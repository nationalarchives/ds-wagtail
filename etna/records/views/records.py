import datetime
import enum
import logging
import urllib.parse

from collections.abc import Mapping
from typing import TypedDict

from django import forms
from django.core.paginator import Page
from django.shortcuts import Http404, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone

from etna.ciim.client import ReturnedResourceIsNotIIIFManifest

from ...ciim.constants import TNA_URLS
from ...ciim.exceptions import DoesNotExist
from ...ciim.paginator import APIPaginator
from .. import iiif
from ..api import records_client

logger = logging.getLogger(__name__)

SEARCH_URL_RETAIN_DELTA = timezone.timedelta(hours=48)


def record_disambiguation_view(request, reference_number):
    """View to render a record's details page or disambiguation page if multiple records are found.

    Details pages differ from all other page types within Etna in that their
    data isn't fetched from the CMS but an external API. And unlike standrard
    Wagtail pages, this view is accessible from a fixed URL.

    Fetches by reference_number may return multiple results.

    For example ADM 223/3. This is both the catalogue reference for 1 piece and
    for the 499 item records within:

    https://discovery.nationalarchives.gov.uk/browse/r/h/C4122893
    """
    per_page = 20
    page_number = int(request.GET.get("page", 1))
    offset = (page_number - 1) * per_page

    result = records_client.search_unified(
        web_reference=reference_number, offset=offset, size=per_page
    )

    if not result:
        raise Http404

    # if the results contain a single record page, redirect to the details page.
    if len(result) == 1:
        record = result.hits[0]
        return record_detail_view(request, record.iaid)

    paginator = APIPaginator(result.total_count, per_page=per_page)
    page = Page(result, number=page_number, paginator=paginator)

    return render(
        request,
        "records/record_disambiguation_page.html",
        {
            "record_results_page": page,
            "queried_reference_number": reference_number,
        },
    )


class HTMLOnlyImage(TypedDict):
    url: str
    width: int | None
    height: int | None


class HTMLOnlyIIIFViewerContext(TypedDict):
    images: list[HTMLOnlyImage]
    source: iiif.ManifestItem
    current_item: int
    item_count: int
    next_page_url: str | None
    prev_page_url: str | None


class ShowRecordViewerOption(enum.Enum):
    NO = "no"
    HTML_ONLY = "html-only"
    JS = "js"


def _get_html_only_iiif_viewer_context(
    *,
    manifest: iiif.IIIFManifest,
    base_url: str,
    canvas_index: int,
    query_params: Mapping[str, str] | None = None,
) -> HTMLOnlyIIIFViewerContext | None:
    """
    Get context required for the HTML-only IIIF viewer.
    """
    if query_params is None:
        query_params = {}

    if not isinstance(canvas_index, int):
        raise ValueError("canvas_index should be an integer.")

    if canvas_index < 0:
        raise ValueError("canvas_index should not be a negative integer.")

    parser = iiif.ManifestParser(manifest=manifest)

    # If canvas_index is bigger than the last index, reset it to 0.
    if canvas_index > parser.get_last_index():
        canvas_index = 0

    next_page_url = None
    prev_page_url = None

    try:
        iiif_item = parser.get_item_at_index(canvas_index)
    except IndexError:
        return None

    try:
        images = parser.get_images_for_item(iiif_item)
    except iiif.ImageNotFoundInItem:
        images = []

    url_parts = list(urllib.parse.urlsplit(base_url))
    url_parts[4] = "record-viewer"

    if canvas_index < parser.get_last_index():
        url_parts[3] = urllib.parse.urlencode(
            {
                **query_params,
                "record_viewer_index": canvas_index + 1,
            }
        )
        next_page_url = urllib.parse.urlunsplit(url_parts)

    if canvas_index >= 1:
        url_parts[3] = urllib.parse.urlencode(
            {
                **query_params,
                "record_viewer_index": canvas_index - 1,
            }
        )
        prev_page_url = urllib.parse.urlunsplit(url_parts)

    return {
        "next_page_url": next_page_url,
        "prev_page_url": prev_page_url,
        "current_item": canvas_index + 1,
        "item_count": parser.get_items_count(),
        "source": iiif_item,
        "images": images,
    }


class RecordDetailViewForm(forms.Form):
    record_viewer_index = forms.IntegerField(required=False, min_value=0)
    show_record_viewer = forms.ChoiceField(
        choices=[
            (v, v)
            for v in [
                ShowRecordViewerOption.JS.value,
                ShowRecordViewerOption.HTML_ONLY.value,
            ]
        ],
        required=False,
    )


def record_detail_view(request, id):
    """View for rendering a record's details page.

    Details pages differ from all other page types within Etna in that their
    data isn't fetched from the CMS but an external API. And unlike pages, this
    view is accessible from a fixed URL.
    Sets context for Back to search button.
    """
    template_name = "records/record_detail.html"
    context = {}
    page_type = "Record details page"

    try:
        # for any record
        record = records_client.fetch(id=id)

        # check archive record
        if record.custom_record_type == "ARCHON":
            page_type = "Archive details page"
            template_name = "records/archive_detail.html"
            context.update(discovery_browse=TNA_URLS.get("discovery_browse"))
        elif record.custom_record_type == "CREATORS":
            page_type = "Record creators page"
            template_name = "records/record_creators.html"
    except DoesNotExist:
        raise Http404

    page_title = f"Catalogue ID: {record.iaid}"
    image = None

    show_record_viewer: ShowRecordViewerOption = ShowRecordViewerOption.NO
    html_only_record_viewer = None
    viewer_index: int | None = None
    iiif_manifest_url: str | None = None

    # Fetch IIIF manifest only if:
    # - The record is digitised
    # - The record is not ARCHON or CREATORS as those templates
    #   don't support IIIF viewer in their templates.
    should_fetch_iiif_manifest = (
        record.is_digitised and record.custom_record_type not in ("ARCHON", "CREATORS")
    )

    if should_fetch_iiif_manifest:
        try:
            # TODO: Use the contents from the request below to fetch the IIIF manifest
            #       in order to build the HTML-only view (progressive enhancement).
            #
            #       Right now this is only used to establish if the record has
            #       a IIIF manifest which could use a HEAD request instead.
            #
            #       We need to know if a record has IIIF manifest in order to establish
            #       if we should load the IIIF viewer to the user. Not all records have
            #       one.
            #
            #       We could make a HEAD request instead to check that, but it feels
            #       short-sighted given that the progressively enhanced view will
            #       require all this content to be fetched anyway.
            #
            #       This information could also be returned in the fetch endpoint
            #       so we know in advance if we need to call the IIIF manifest
            #       endpoint at all. The raised ticket:
            #       https://national-archives.atlassian.net/browse/DOR-53
            iiif_manifest = records_client.fetch_iiif_manifest(id=record.iaid)
        except DoesNotExist:
            pass
        except ReturnedResourceIsNotIIIFManifest:
            logger.warning(
                "Expected to fetch an IIIF manifest, but received something else.",
                exc_info=True,
            )
        except Exception:
            logger.warning(
                "Unexpected error happened when trying to fetch the IIIF manifest for a record: iaid=%s",
                record.iaid,
                exc_info=True,
            )
        else:
            iiif_manifest_url = records_client.get_public_iiif_manifest_url(
                id=record.iaid
            )
            show_record_viewer = ShowRecordViewerOption.JS
            view_form = RecordDetailViewForm(request.GET)
            if view_form.is_valid():
                try:
                    show_record_viewer = (
                        ShowRecordViewerOption(
                            view_form.cleaned_data["show_record_viewer"]
                        )
                        or show_record_viewer
                    )
                except ValueError:
                    pass
                viewer_index = view_form.cleaned_data["record_viewer_index"] or 0
                query_params = {}
                if view_form.cleaned_data["show_record_viewer"] is not None:
                    # We only want to pass the query params that are output by application
                    # if possible to avoid user being able to insert arbitrary data to the
                    # template renderer.
                    query_params["show_record_viewer"] = view_form.cleaned_data[
                        "show_record_viewer"
                    ]
                html_only_record_viewer = _get_html_only_iiif_viewer_context(
                    manifest=iiif_manifest,
                    base_url=request.get_full_path(),
                    canvas_index=viewer_index,
                    query_params=query_params,
                )

    # Back to search - default url
    back_to_search_url = reverse("search-featured")

    # Back to search button - update url when timestamp is not expired

    if back_to_search_url_timestamp := request.session.get(
        "back_to_search_url_timestamp"
    ):
        back_to_search_url_timestamp = datetime.datetime.fromisoformat(
            back_to_search_url_timestamp
        )

        if timezone.now() <= (back_to_search_url_timestamp + SEARCH_URL_RETAIN_DELTA):
            back_to_search_url = request.session.get("back_to_search_url")

    context.update(
        html_only_record_viewer=html_only_record_viewer,
        iiif_manifest_url=iiif_manifest_url,
        canvas_index=viewer_index,
        image=image,
        record=record,
        show_record_viewer=show_record_viewer is not ShowRecordViewerOption.NO,
        show_js_record_viewer=show_record_viewer is ShowRecordViewerOption.JS,
        meta_title=record.summary_title,
        back_to_search_url=back_to_search_url,
        page_type=page_type,
        page_title=page_title,
    )

    # Note: This page uses cookies to render GTM, please ensure to keep TemplateResponse or similar when changed.
    return TemplateResponse(request=request, template=template_name, context=context)
