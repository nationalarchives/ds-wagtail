from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Page
from wagtail.admin.forms.choosers import BaseFilterForm, SearchFilterMixin
from wagtail.admin.views.generic import chooser as chooser_views
from wagtail.admin.viewsets.chooser import ChooserViewSet
from django.shortcuts import Http404
from django.urls import re_path
from generic_chooser.views import BaseChosenView, ChooserMixin, ChooserViewSet

from etna.ciim.client import Stream
from etna.ciim.exceptions import ClientAPIError
from etna.ciim.paginator import APIPaginator

from ..api import records_client
from ..models import Record
from ..widgets import RecordChooser


class SearchForm(SearchFilterMixin, BaseFilterForm):
    pass

  
class RecordMixin:
    model = Record
    filter_form_class = SearchForm
    is_searchable = True

    def get_object(self, pk):
        try:
            return records_client.fetch(iaid=pk)
        except KongAPIError:
            raise ObjectDoesNotExist

    def get_objects(self, pks):
        return records_client.fetch_all(iaids=pks)

    def get_object_id(self, instance):
        return instance.iaid

    def get_edit_item_url(self, instance):
        # Avoid trying to show 'edit' links for records
        return None

    def can_create(self):
        # Avoid showing 'create' options for records
        return False

    def get_results_page(self, request):
        page_number = int(request.GET.get("p", 1))

        query = request.GET.get("q", "")
        if query:
            results = records_client.search_unified(
                q=query,
                stream=Stream.EVIDENTIAL,
                size=self.per_page,
                offset=((page_number - 1) * self.per_page,),
            )
            count = results.total_count
        else:
            results = []
            count = 0

        paginator = APIPaginator(count, self.per_page)
        return Page(results, page_number, paginator)


class RecordChooseView(RecordMixin, chooser_views.ChooseView):
    pass


class RecordChooseResultsView(RecordMixin, chooser_views.ChooseResultsView):
    pass

class RecordChosenView(RecordMixin, chooser_views.ChosenView):
    pass

class RecordChosenMultipleView(RecordMixin, chooser_views.ChosenMultipleView):
    pass


class RecordChooserViewSet(ChooserViewSet):
    """Custom chooser to allow users to filter and select records."""

    icon = "form"
    model = Record
    choose_view_class = RecordChooseView
    choose_results_view_class = RecordChooseResultsView
    chosen_view_class = RecordChosenView
    chosen_multiple_view_class = RecordChosenMultipleView
    widget_class = RecordChooser
    page_title = "Choose a record"
    per_page = 15
    register_widget = False
