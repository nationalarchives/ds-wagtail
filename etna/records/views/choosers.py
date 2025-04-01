from django.core.paginator import Page
from django.shortcuts import Http404
from django.urls import re_path
from generic_chooser.views import BaseChosenView, ChooserMixin, ChooserViewSet

from etna.ciim.client import Stream
from etna.ciim.exceptions import ClientAPIError
from etna.ciim.paginator import APIPaginator

from ..api import records_client
from ..models import Record
from django.conf import settings


class ClientAPIModelChooserMixinIn(ChooserMixin):
    """Chooser source to allow filtering and selection of Client API model data.

    Similar to the DFRDRFChooserMixin:

    https://github.com/wagtail/wagtail-generic-chooser/blob/9ec9db937fe40311c67ed055e1b3f0dcd1b86908/generic_chooser/views.py#L223
    """

    # Model belonging to this chooser, set via <model>ChooserViewSet.
    model: Record = None

    # Allow models to be searched via chooser. Hides the search box if False
    is_searchable = True

    def get_paginated_object_list(self, page_number, search_term="", **kwargs):
        offset = ((page_number - 1) * self.per_page,)
        count = 0
        results = []

        if search_term:
            results = records_client.search_unified(
                q=search_term,
                stream=Stream.EVIDENTIAL,
                size=self.per_page,
                offset=offset,
            )
            count = results.total_count

        paginator = APIPaginator(count, self.per_page)
        page = Page(results, page_number, paginator)
        return (page, paginator)

    def get_object(self, pk):
        """Fetch selected object"""
        return records_client.fetch(iaid=pk)

    def get_object_id(self, instance):
        """Return selected object's ID, used when resolving a link to this item.

        see RecordChooserViewSet.get_urlpatterns for overridden pattern for selected item.
        """
        return instance.iaid

    def user_can_create(self, user):
        """Records cannot be created in Wagtail.

        Hides the "create" tab in chooser.
        """
        return False



from django.views.generic.base import View
import requests

from wagtail.admin.ui.tables import Column, TitleColumn
from wagtail.admin.views.generic.chooser import (
    BaseChooseView, ChooseViewMixin, ChooseResultsViewMixin, ChosenResponseMixin, ChosenViewMixin, CreationFormMixin
)
from wagtail.admin.viewsets.chooser import ChooserViewSet
from wagtail.admin.widgets import BaseChooser
from wagtail.admin.forms.choosers import BaseFilterForm
from django import forms
from django.core.paginator import Page, Paginator

class APIPaginator(Paginator):
    """
    Customisation of Django's Paginator class for use when we don't want it to handle
    slicing on the result set, but still want it to generate the page numbering based
    on a known result count.
    """
    def __init__(self, count, per_page, **kwargs):
        self._count = int(count)
        super().__init__([], per_page, **kwargs)

    @property
    def count(self):
        return self._count

class APIFilterForm(BaseFilterForm):
    q = forms.CharField(
        label="Search",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search"}),
    )
    
    def filter(self, objects):
        search_query = self.cleaned_data.get("q")
        if search_query:
            objects = BaseRecordChooseView.get_results_page(self, query=search_query)
        else:
            objects = BaseRecordChooseView.get_results_page(self)
        return objects

class BaseRecordChooseView(BaseChooseView):
    filter_form_class = APIFilterForm

    @property
    def columns(self):
        return [
            TitleColumn(
                "iaid",
                label="IAID",
                accessor='@template.details.iaid',
                id_accessor='@template.details.iaid',
                url_name=self.chosen_url_name,
                link_attrs={"data-chooser-modal-choice": True},
            ),
            Column(
                "title", label="Title", accessor="@template.details.summaryTitle"
            )
        ]

    def get_object_list(self, query="*"):
        page = 1
        params = {
            "q": query,
            "size": self.per_page,
            "from": (page - 1) * self.per_page,
            "sort": "",
            "sortOrder": "asc",
        }

        r = requests.get(f"{settings.CLIENT_BASE_URL}/search", params=params)
        r.raise_for_status()
        results = r.json()
        results = results.get("data", [])
        return results

    def apply_object_list_ordering(self, objects):
        return objects
    
    def get_results_page(self, request, query="*"):
        try:
            page_number = int(request.GET.get('p', 1))
        except ValueError:
            page_number = 1

        query = request.GET.get('q', query)

        params = {
            "q": query,
            "from": (page_number - 1) * self.per_page,
            "sort": "",
            "sortOrder": "asc",
            "size": self.per_page,
        }

        r = requests.get(f"{settings.CLIENT_BASE_URL}/search", params=params)
        r.raise_for_status()
        result = r.json()
        paginator = APIPaginator(result['stats']['total'], self.per_page)
        page = Page(result.get("data", []), page_number, paginator)

        return page

class RecordChooseView(ChooseViewMixin, CreationFormMixin, BaseRecordChooseView):
    pass


class RecordChooseResultsView(ChooseResultsViewMixin, CreationFormMixin, BaseRecordChooseView):
    pass


class RecordChosenViewMixin(ChosenViewMixin):
    def get_object(self, pk):
        r = requests.get(f"{settings.CLIENT_BASE_URL}/get?id={pk}")
        r.raise_for_status()
        result = r.json()
        result = result.get("data", [])[0].get("@template", {}).get("details", {})
        return result


class RecordChosenResponseMixin(ChosenResponseMixin):
    def get_chosen_response_data(self, item):
        return {
            "id": item.get("iaid"),
            "title": f"{item["summaryTitle"]} ({item["iaid"]})",
        }


class RecordChosenView(RecordChosenViewMixin, RecordChosenResponseMixin, View):
    pass


class BaseRecordChooserWidget(BaseChooser):
    def get_instance(self, value):
        if value is None:
            return None
        elif isinstance(value, dict):
            return value
        else:
            r = requests.get(f"{settings.CLIENT_BASE_URL}/get?id={value}")
            result = r.json()
            result = result.get("data", [])[0].get("@template", {}).get("details", {})
            return result

    def get_value_data_from_instance(self, instance):
        return {
            "id": instance["iaid"],
            "title": f"{instance["summaryTitle"]} ({instance["iaid"]})",
        }
    
    chooser_modal_url_name = "record_chooser:choose"


class RecordChooserViewSet(ChooserViewSet):
    icon = "form"
    choose_one_text = "Choose a record"
    choose_another_text = "Choose another record"
    edit_item_text = "Edit this record"

    choose_view_class = RecordChooseView
    choose_results_view_class = RecordChooseResultsView
    chosen_view_class = RecordChosenView
    base_widget_class = BaseRecordChooserWidget


record_chooser_viewset = RecordChooserViewSet("record_chooser", url_prefix="record-chooser")


# class ClientAPIChosenView(BaseChosenView):
#     """View to handle fetching a selected item."""

#     def get(self, request, pk):
#         """Fetch selected item by its pk (in our case IAID)

#         Override parent to handle any errors from the Client API.
#         """
#         try:
#             return super().get(request, pk)
#         except ClientAPIError:
#             raise Http404


# class RecordChooserViewSet(ChooserViewSet):
#     """Custom chooser to allow users to filter and select records."""

#     model = Record
#     icon = "form"
#     choose_one_text = "Choose a record"
#     choose_another_text = "Choose another record"




    # base_chosen_view_class = ClientAPIChosenView
    # chooser_mixin_class = ClientAPIModelChooserMixinIn
    # icon = "form"
    # model = Record
    # page_title = "Choose a record"
    # per_page = 10

    # def get_choose_view_attrs(self):
    #     attrs = super().get_choose_view_attrs()
    #     attrs.update(model=self.model)
    #     return attrs

    # def get_chosen_view_attrs(self):
    #     attrs = super().get_chosen_view_attrs()
    #     attrs.update(model=self.model)
    #     return attrs

    # def get_urlpatterns(self):
    #     """Define patterns for chooser and chosen views.

    #     Overridden to allow IAID to be used as an ID for chosen view"""
    #     return super().get_urlpatterns() + [
    #         re_path(r"^$", self.choose_view, name="choose"),
    #         re_path(r"^([\w-]+)/$", self.chosen_view, name="chosen"),
    #     ]
