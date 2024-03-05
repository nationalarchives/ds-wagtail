from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock

from .models import RecordSeries
from .utils import get_series_search_results_url


class RecordSeriesBlock(blocks.StructBlock):
    record_series = SnippetChooserBlock(RecordSeries)

    class Meta:
        template = "series/blocks/series_block.html"
        help_text = "Promote a series of records."
        icon = "folder"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        record_series = value.get("record_series")
        if record_series is not None:
            context['record_series'] = record_series
            context["record_series_url"] = get_series_search_results_url(record_series)
        return context
