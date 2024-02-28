from django.core.paginator import Page
from django.shortcuts import Http404
from django.urls import re_path
from generic_chooser.views import BaseChosenView, ChooserMixin, ChooserViewSet

from ...ciim.client import Stream
from ...ciim.exceptions import ClientAPIError
from ...ciim.paginator import APIPaginator
from ..api import records_client
from ..models import Record


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


class ClientAPIChosenView(BaseChosenView):
    """View to handle fetching a selected item."""

    def get(self, request, pk):
        """Fetch selected item by its pk (in our case IAID)

        Override parent to handle any errors from the Client API.
        """
        try:
            return super().get(request, pk)
        except ClientAPIError:
            raise Http404


class RecordChooserViewSet(ChooserViewSet):
    """Custom chooser to allow users to filter and select records."""

    base_chosen_view_class = ClientAPIChosenView
    chooser_mixin_class = ClientAPIModelChooserMixinIn
    icon = "form"
    model = Record
    page_title = "Choose a record"
    per_page = 10

    def get_choose_view_attrs(self):
        attrs = super().get_choose_view_attrs()
        attrs.update(model=self.model)
        return attrs

    def get_chosen_view_attrs(self):
        attrs = super().get_chosen_view_attrs()
        attrs.update(model=self.model)
        return attrs

    def get_urlpatterns(self):
        """Define patterns for chooser and chosen views.

        Overridden to allow IAID to be used as an ID for chosen view"""
        return super().get_urlpatterns() + [
            re_path(r"^$", self.choose_view, name="choose"),
            re_path(r"^([\w-]+)/$", self.chosen_view, name="chosen"),
        ]
