from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Highlight
from .views import HighlightChooserViewSet


class HighlightViewSet(SnippetViewSet):
    icon = "doc-full"
    list_display = ["title", "reference_number", "dates"]
    menu_label = "Highlights"
    menu_name = "highlights"
    menu_order = 400
    add_to_admin_menu = True
    chooser_viewset_class = HighlightChooserViewSet


register_snippet(Highlight, viewset=HighlightViewSet)
