from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail.admin.viewsets.chooser import ChooserViewSet
from wagtail.admin.viewsets.model import ModelViewSet

from .models import Series


class SeriesViewSet(ModelViewSet):
    filter_list = ["category"]
    icon = "folder"
    inspect_view_enabled = True
    list_display = ["admin_name", UpdatedAtColumn()]
    list_filter = ["category"]
    model = Series


series_viewset = SeriesViewSet("series")


class SeriesChooserViewSet(ChooserViewSet):
    choose_another_text = "Choose another series"
    choose_one_text = "Choose a series"
    edit_item_text = "Edit this series"
    icon = "folder"
    model = Series


series_chooser_viewset = SeriesChooserViewSet("series_chooser")
