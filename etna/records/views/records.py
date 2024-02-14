import logging
import datetime
from typing import Any

from django.core.paginator import Page
from django.shortcuts import Http404, render
from django.template.response import TemplateResponse
from django import http
from django.urls import reverse
from django.utils import timezone
from wagtail.admin.urls import TemplateView

from etna.records import iiif
from etna.records.models import Image, Record

from ...ciim.constants import TNA_URLS
from ...ciim.exceptions import DoesNotExist
from ...ciim.paginator import APIPaginator
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

    # if the results contain a single record page, render the details page.
    if len(result) == 1:
        record = result.hits[0]
        return RecordDetailInlineView.as_view()(request, record.iaid)

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


class RecordDetailView(TemplateView):
    template_name = "records/record_detail.html"
    record: Record

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.response.HttpResponseBase:
        self.record = self.get_record()
        return super().dispatch(request, *args, **kwargs)

    def get_record(self) -> Record:
        try:
            return records_client.fetch(id=self.kwargs['id'])
        except DoesNotExist:
            raise Http404

    def get_template_names(self) -> list[str]:
        # check archive record
        if self.record.custom_record_type == "ARCHON":
            return ["records/archive_detail.html"]
        elif self.record.custom_record_type == "CREATORS":
            return ["records/record_creators.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["back_to_search_url"] = self.get_back_to_search_url()
        context["discovery_browse"] = self.get_discovery_browse_url()
        context["image"] = self.get_image() 
        context["meta_title"] = self.record.summary_title
        context["page_title"] = f"Catalogue ID: {self.record.iaid}"
        context["page_type"] = self.get_page_type()
        context["record"] = self.record
        return context
    
    def get_discovery_browse_url(self) -> str | None:
        if self.record.custom_record_type == "ARCHON":
            return TNA_URLS.get("discovery_browse")
        return None
    
    def get_image(self) -> Image | None:
        # TODO: Client API open beta API does not support media. Re-enable/update once media is available.
        # if page.is_digitised:
        #     image = Image.search.filter(rid=page.media_reference_id).first()
        return None
    
    def get_back_to_search_url(self) -> str:
        # Back to search button - update url when timestamp is not expired
        if back_to_search_url_timestamp := self.request.session.get(
            "back_to_search_url_timestamp"
        ):
            back_to_search_url_timestamp = datetime.datetime.fromisoformat(
                back_to_search_url_timestamp
            )

            if timezone.now() <= (back_to_search_url_timestamp + SEARCH_URL_RETAIN_DELTA):
                return self.request.session.get("back_to_search_url")

        # Back to search - default url
        return reverse("search-featured")
    
    def get_page_type(self) -> str:
        match self.record.custom_record_type:
            case "ARCHON":
                return "Archive details page"
            case "CREATORS":
                return "Record creators page"
        return "Record details page"

    
class IIIFManifestRecordDetailView(RecordDetailView):
    def get_iiif_manifest_url(self, record: Record) -> str | None:
        try:
            return iiif.manifest_url_for_record(record)
        except (iiif.RecordHasNoManifest, iiif.RecordManifestUnexpectedlyUnavailable):
            return None
        except Exception:
            logger.warning("Unexpected error when getting the IIIF manifest URL for record: record_iaid=%s", record.iaid, exc_info=True)
            raise

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        iiif_manifest_url = self.get_iiif_manifest_url(self.record)
        if iiif_manifest_url is not None:
            context["iiif_manifest_url"] = iiif_manifest_url
        return context


class RecordDetailInlineView(IIIFManifestRecordDetailView):
    template_name = "records/record_detail_inline.html"


class RecordDetailFullView(IIIFManifestRecordDetailView):
    template_name = "records/record_detail_full.html"