# from django.core.paginator import Page
# from django.views.generic.base import View
# from wagtail.admin.ui.tables import Column, TitleColumn
# from wagtail.admin.views.generic.chooser import (
#     BaseChooseView,
#     ChooseResultsViewMixin,
#     ChooseViewMixin,
#     CreationFormMixin,
# )
# from wagtail.admin.viewsets.chooser import ChooserViewSet

# from .client import CIIMClient
# from .forms import APIFilterForm
# from .mixins import (
#     RecordChosenResponseMixin,
#     RecordChosenViewMixin,
# )
# from .pagination import APIPaginator
# from .widgets import BaseRecordChooserWidget


# class BaseRecordChooseView(BaseChooseView):
#     filter_form_class = APIFilterForm
#     paginator = APIPaginator

#     @property
#     def columns(self):
#         return [
#             TitleColumn(
#                 "iaid",
#                 label="IAID",
#                 accessor="@template.details.iaid",
#                 id_accessor="@template.details.iaid",
#                 url_name=self.chosen_url_name,
#                 link_attrs={"data-chooser-modal-choice": True},
#             ),
#             Column("title", label="Title", accessor="@template.details.summaryTitle"),
#         ]

#     def apply_object_list_ordering(self, objects):
#         return objects

#     def get_results_page(self, request, query="*"):
#         try:
#             page_number = int(request.GET.get("p", 1))
#         except ValueError:
#             page_number = 1

#         query = request.GET.get("q", query)

#         params = {
#             "q": query,
#             "from": (page_number - 1) * self.per_page,
#             "sort": "",
#             "sortOrder": "asc",
#             "size": self.per_page,
#         }

#         client = CIIMClient(params=params)
#         results, pagination = client.get_record_list()
#         paginator = APIPaginator(pagination, self.per_page)
#         return Page(results, page_number, paginator)

import re
from queryish.rest import APIModel, APIQuerySet
from wagtail.admin.viewsets.chooser import ChooserViewSet
from django.conf import settings
import requests


class RecordQuerySet(APIQuerySet):
    """
    Custom queryset for interacting with the CIIM API.
    """
    base_url = settings.ROSETTA_API_URL + "search?q=*"
    detail_url = settings.ROSETTA_API_URL + "get?id=%s"
    fields = ["@template.details.iaid", "summaryTitle"]
    pagination_style = "offset-limit"
    verbose_name_plural = "records"
    http_headers = {}
    pk_field_name = "iaid"

    def fetch_api_response(self, url=None, params=None):
        # construct a hashable key for the params
        if url is None:
            url = self.base_url

        if params is None:
            params = {}
        key = tuple([url] + sorted(params.items()))
        if key not in self._responses:
            self._responses[key] = requests.get(
                url,
                params=params,
                headers=self.http_headers,
            ).json()
        print(requests.get(
                url,
                params=params,
                headers=self.http_headers,
            ).url)
        return self._responses[key]

    def get_results_from_response(self, response):
        return response.get("data", [])
    
    def run_count(self):
        params = self.get_filters_as_query_dict()

        if self.pagination_style == "offset-limit" or self.pagination_style == "page-number":
            if self.pagination_style == "offset-limit":
                params[self.limit_query_param] = 1
            else:
                params[self.page_query_param] = 1

            response_json = self.fetch_api_response(params=params)
            print(response_json)
            
            count = response_json["stats"]["results"]
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
        url = settings.ROSETTA_API_URL + "get?id="
        print(data)
        return cls(
            iaid=data['@template']['details']['iaid'],
            summaryTitle=data['@template']['details']['title'],
        )

    @classmethod
    def from_individual_data(cls, data):
        data = data["data"][0]
        print(data)
        return cls(
            iaid=data['@template']['details']['iaid'],
            summaryTitle=data['@template']['details']['title'],
        )
    

class RecordChooserViewSet(ChooserViewSet):
    model = Record

    choose_one_text = "Choose a record"
    choose_another_text = "Choose another record"


record_chooser_viewset = RecordChooserViewSet("record_chooser")