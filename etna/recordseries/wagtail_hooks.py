from wagtail.snippets.models import register_snippet

from .admin_views import RecordSeriesSnippetViewSet

register_snippet(RecordSeriesSnippetViewSet)
