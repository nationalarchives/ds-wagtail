from typing import Any, Dict, List
from django.core.paginator import Page
from django.http import HttpRequest, HttpResponse, Http404
from django.views.generic import TemplateView

from ...analytics.mixins import DataLayerMixin
from ...ciim import kong_client
from ...ciim.utils import LazyResultList, MinimalResultParser, find_all
from ...ciim.exceptions import KongAmbiguousRecordIdentifier, KongRecordNotFound
from ...ciim.paginator import APIPaginator


class DetailResultParser(MinimalResultParser):
    """
    A custom parser used by `RecordDetailView` to apply some additional
    tidy-up to the record representation from Kong.
    """

    def __call__(self, value):
        # apply minimal parsing first
        data = super().__call__(value)

        # add simple topic list
        data["topics"] = [
            {
                "title": topic["summary"]["title"],
            }
            for topic in data.get("topic", ())
        ]

        try:
            data["multimedia_id"] = data["multimedia"]["@admin"]["id"]
        except KeyError:
            pass

        try:
            data["next_record"] = {"iaid": data["@next"]["@admin"]["id"]}
        except KeyError:
            pass

        try:
            data["previous_record"] = {"iaid": data["@previous"]["@admin"]["id"]}
        except KeyError:
            pass

        # simplify parent data
        if parent := data.pop("parent", None):
            try:
                data["parent"] = {
                    "iaid": parent["@admin"]["id"],
                    "reference_number": parent["identifier"][0]["reference_number"],
                    "title": parent["summary"]["title"],
                }
            except(IndexError, KeyError):
                pass

        # simplify hierarchy data
        if hierarchy := data.pop("hierarchy", None):
            try:
                data["hierarchy"] = [
                    {
                        "reference_number": ancestor["identifier"][0]["reference_number"],
                        "title": ancestor["summary"]["title"],
                    }
                    for ancestor in hierarchy[0]
                    if "identifier" in ancestor
                ]
            except(IndexError, KeyError):
                pass

        # simplify availability data
        if delivery := data.get("availability", {}).get("delivery", {}):
            try:
                data["availability_delivery_condition"] = delivery["condition"][
                    "value"
                ]
            except KeyError:
                pass
            try:
                data["availability_delivery_surrogates"] = delivery["surrogate"]
            except KeyError:
                pass


        # simplify related data
        if related := data.pop("related", None):
            related_records = find_all(
                related,
                predicate=lambda x: x["@link"]["relationship"]["value"] == "related",
            )
            data["related_records"] = [
                {
                    "title": record["summary"]["title"],
                    "iaid": record["@admin"]["id"],
                }
                for record in related_records
            ]

            related_articles = find_all(
                related, predicate=lambda i: i["@admin"]["source"] == "wagtail-es"
            )
            data["related_articles"] = [
                {"title": article["summary"]["title"], "url": article["source"]["location"]}
                for article in related_articles
                if "summary" in article
            ]

        return data


class RecordDisabiguationView(TemplateView):
    """View to render a record's details page or disambiguation page if multiple records are found.

    Details pages differ from all other page types within Etna in that their
    data isn't fetched from the CMS but an external API. And unlike standrard
    Wagtail pages, this view is accessible from a fixed URL.

    Fetches by reference_number may return multiple results.

    For example ADM 223/3. This is both the catalogue reference for 1 piece and
    for the 499 item records within:

    https://discovery.nationalarchives.gov.uk/browse/r/h/C4122893
    """

    http_method_names = ["get"]
    paginate_by = 20
    template_name = "records/record_disambiguation_page.html"

    def get(self, request, web_reference: str) -> HttpResponse:
        try:
            page_number = int(request.GET.get("page", 1))
        except TypeError:
            raise Http404(f"'{request.GET['page']}' is not a valid page number.")

        api_result = self.get_api_result(web_reference, page_number)
        context_data = {"queried_reference_number": web_reference}

        if not api_result.total_count:
            raise Http404(f"No matches found for '{web_reference}'.")

        if not api_result:
            raise Http404(f"Page {page_number} contained zero results.")

        if api_result.total_count == 1:
            view = RecordDetailView.as_view()
            return view(request, api_result[0]["iaid"])

        # NOTE: We create a paginator here whether it is needed or not. Because,
        # unlike a regular Django paginator, no database query is needed to
        # calculate the total, and generation uses very few resources
        paginator = APIPaginator(api_result.total_count, per_page=self.paginate_by)
        page = Page(list(api_result), number=page_number, paginator=paginator)
        context_data.update(
            is_paginated=api_result.total_count > self.paginate_by,
            paginator=paginator,
            page_obj=page,
            object_list=page.object_list,
        )

        # Allow get_context_data() to include our
        # 'context_data' in in the template
        self.extra_context = context_data

        # Render to the template
        return super().get(request, web_reference)

    def get_api_result(self, web_reference, page_number) -> LazyResultList:
        offset = (page_number - 1) * self.paginate_by
        return kong_client.search_unified(
            web_reference=web_reference, offset=offset, size=self.paginate_by
        )


class RecordDetailView(DataLayerMixin, TemplateView):
    """
    View for rendering a specific record.
    """

    http_method_names = ["get"]
    template_name = "records/record_detail.html"

    def get(self, request, iaid) -> HttpResponse:
        self.record = self.get_record_details(iaid)
        self.extra_context = {"record": self.record}
        return super().get(request, iaid)

    def get_record_details(self, iaid):
        try:
            # Providing out
            return kong_client.fetch(iaid=iaid, expand=True, result_parser=DetailResultParser)
        except KongAmbiguousRecordIdentifier:
            raise Http404(f"Multiple records found for iaid '{iaid}'")
        except KongRecordNotFound:
            raise Http404(f"No records found for iaid '{iaid}'")

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        # TODO: Modify the return value based on self.record
        return super().get_datalayer_data(request)

    def get_template_names(self) -> List[str]:
        # TODO: Modify the return value based on self.record
        return super().get_template_names()
