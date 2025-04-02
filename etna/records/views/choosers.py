from django.core.paginator import Page
from django.conf import settings

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
