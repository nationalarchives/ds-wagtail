import requests
from django.conf import settings
from django.utils.html import strip_tags
from queryish.rest import APIModel, APIQuerySet
from wagtail.admin.views.generic.chooser import (
    ChooseView,
)
from wagtail.admin.viewsets.chooser import ChooserViewSet

from .forms import APIFilterForm


class BaseRecordChooseView(ChooseView):
    """
    A view for choosing records from the CIIM API.
    """

    filter_form_class = APIFilterForm


class RecordQuerySet(APIQuerySet):
    """
    Custom queryset for interacting with the CIIM API.
    """

    base_url = settings.ROSETTA_API_URL + "search"
    detail_url = settings.ROSETTA_API_URL + "get?id=%s"
    fields = ["iaid", "title"]
    pagination_style = "offset-limit"
    verbose_name_plural = "records"
    http_headers = {}
    pk_field_name = "iaid"
    offset_query_param = "from"
    limit_query_param = "limit"
    page_size = 10

    def fetch_api_response(self, url=None, params=None):
        # construct a hashable key for the params
        if url is None:
            url = self.base_url

        if params is None:
            params = {}

        if not params.get("q", None):
            params["q"] = "*"
        key = tuple([url] + sorted(params.items()))
        if key not in self._responses:
            self._responses[key] = requests.get(
                url,
                params=params,
                headers=self.http_headers,
            ).json()
        return self._responses[key]

    def get_results_from_response(self, response):
        return response.get("data", [])

    def run_count(self):
        params = self.get_filters_as_query_dict()

        if (
            self.pagination_style == "offset-limit"
            or self.pagination_style == "page-number"
        ):
            if self.pagination_style == "offset-limit":
                params[self.limit_query_param] = 1
            else:
                params[self.page_query_param] = 1

            response_json = self.fetch_api_response(params=params)

            count = response_json["stats"]["total"]
            # count is the full result set without considering slicing;
            # we need to adjust it to the slice
            if self.limit is not None:
                count = min(count, self.limit)
            count = max(0, count - self.offset)
            return count


class Record(APIModel):
    base_query_class = RecordQuerySet
    pk_field_name = "iaid"

    @classmethod
    def from_query_data(cls, data):
        return cls(
            iaid=data["@template"]["details"]["iaid"],
            title=strip_tags(data["@template"]["details"].get("summaryTitle", None)),
            reference_number=data["@template"]["details"].get("referenceNumber", None),
        )

    @classmethod
    def from_individual_data(cls, data):
        data = data["data"][0]
        return cls(
            iaid=data["@template"]["details"]["iaid"],
            title=strip_tags(data["@template"]["details"].get("title", None)),
            reference_number=data["@template"]["details"].get("referenceNumber", None),
        )

    def __str__(self):
        return f"{self.title} ({self.reference_number} / {self.iaid})"

    class Meta:
        fields = [
            "iaid",
            "title",
            "reference_number",
        ]


class RecordChooserViewSet(ChooserViewSet):
    model = Record
    url_filter_parameters = ["q"]
    preserve_url_parameters = ["q"]
    per_page = 10
    choose_one_text = "Choose a record"
    choose_another_text = "Choose another record"
    search_tab_label = "Search"
    choose_view_class = BaseRecordChooseView


record_chooser_viewset = RecordChooserViewSet("record_chooser")
