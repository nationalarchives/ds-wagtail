from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import RecordSeries


class RecordSeriesSnippetViewSet(SnippetViewSet):
    icon = "folder"
    inspect_view_enabled = True
    list_display = ["admin_name", UpdatedAtColumn()]
    list_filter = ["show_only_digitised_records"]
    model = RecordSeries
