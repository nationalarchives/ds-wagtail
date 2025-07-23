from django.core.paginator import Page
from django.views.generic.base import View
from wagtail.admin.ui.tables import Column, TitleColumn
from wagtail.admin.views.generic.chooser import (
    BaseChooseView,
    ChooseResultsViewMixin,
    ChooseViewMixin,
    CreationFormMixin,
)
from wagtail.admin.viewsets.chooser import ChooserViewSet

from .client import CIIMClient
from .forms import APIFilterForm
from .mixins import (
    RecordChosenResponseMixin,
    RecordChosenViewMixin,
)
from .pagination import APIPaginator
from .widgets import BaseRecordChooserWidget


class BaseRecordChooseView(BaseChooseView):
    filter_form_class = APIFilterForm
    paginator = APIPaginator

    @property
    def columns(self):
        return [
            TitleColumn(
                "iaid",
                label="IAID",
                accessor="@template.details.iaid",
                id_accessor="@template.details.iaid",
                url_name=self.chosen_url_name,
                link_attrs={"data-chooser-modal-choice": True},
            ),
            Column("title", label="Title", accessor="@template.details.summaryTitle"),
        ]

    def apply_object_list_ordering(self, objects):
        return objects

    def get_results_page(self, request, query="*"):
        try:
            page_number = int(request.GET.get("p", 1))
        except ValueError:
            page_number = 1

        query = request.GET.get("q", query)

        params = {
            "q": query,
            "from": (page_number - 1) * self.per_page,
            "sort": "",
            "sortOrder": "asc",
            "size": self.per_page,
        }

        client = CIIMClient(params=params)
        results, pagination = client.get_record_list()
        paginator = APIPaginator(pagination, self.per_page)
        return Page(results, page_number, paginator)


class RecordChooseView(ChooseViewMixin, CreationFormMixin, BaseRecordChooseView):
    pass


class RecordChooseResultsView(
    ChooseResultsViewMixin, CreationFormMixin, BaseRecordChooseView
):
    pass


class RecordChosenView(RecordChosenViewMixin, RecordChosenResponseMixin, View):
    pass


class RecordChooserViewSet(ChooserViewSet):
    icon = "form"
    choose_one_text = "Choose a record"
    choose_another_text = "Choose another record"
    edit_item_text = "Edit this record"

    choose_view_class = RecordChooseView
    choose_results_view_class = RecordChooseResultsView
    chosen_view_class = RecordChosenView
    base_widget_class = BaseRecordChooserWidget


record_chooser_viewset = RecordChooserViewSet(
    "record_chooser", url_prefix="record-chooser"
)
