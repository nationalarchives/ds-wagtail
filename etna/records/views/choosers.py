from django.conf.urls import url
from django.shortcuts import Http404

from generic_chooser.views import BaseChosenView, ChooserMixin, ChooserViewSet

from ...ciim.client import Stream
from ...ciim.exceptions import KongException
from ..models import Record


class KongModelChooserMixinIn(ChooserMixin):
    """Chooser source to allow filtering and selection of Kong model data.

    Similar to the DFRDRFChooserMixin:

    https://github.com/wagtail/wagtail-generic-chooser/blob/9ec9db937fe40311c67ed055e1b3f0dcd1b86908/generic_chooser/views.py#L223
    """

    # Model belonging to this chooser, set via <model>ChooserViewSet.
    model = None

    # Allow models to be searched via chooser. Hides the search box if False
    is_searchable = True

    def get_object_list(self, search_term=""):
        """Filter object list by user's search term"""
        return self.model.search.filter(keyword=search_term, stream=Stream.EVIDENTIAL)

    def get_object(self, pk):
        """Fetch selected object"""
        return self.model.search.get(iaid=pk)

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


class KongChosenView(BaseChosenView):
    """View to handle fetching a selected item."""

    def get(self, request, pk):
        """Fetch selected item by its pk (in our case IAID)

        Override parent to handle any errors from the Kong API.
        """
        try:
            return super().get(request, pk)
        except KongException:
            raise Http404


class RecordChooserViewSet(ChooserViewSet):
    """Custom chooser to allow users to filter and select records."""

    base_chosen_view_class = KongChosenView
    chooser_mixin_class = KongModelChooserMixinIn
    icon = "form"
    model = Record
    page_title = "Choose a record"
    per_page = 10

    def get_choose_view_attrs(self):
        attrs = super().get_choose_view_attrs()
        if hasattr(self, "model"):
            attrs["model"] = self.model

        return attrs

    def get_chosen_view_attrs(self):
        attrs = super().get_chosen_view_attrs()
        attrs.update(model=self.model)
        return attrs

    def get_urlpatterns(self):
        """Define patterns for chooser and chosen views.

        Overridden to allow IAID to be used as an ID for chosen view"""
        return super().get_urlpatterns() + [
            url(r"^$", self.choose_view, name="choose"),
            url(r"^([\w-]+)/$", self.chosen_view, name="chosen"),
        ]
