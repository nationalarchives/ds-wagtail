from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from etna.series.models import Series

from .admin_views import series_chooser_viewset
from .utils import get_series_search_results_url

SeriesChooserBlock = series_chooser_viewset.get_block_class(
    name="SeriesChooserBlock", module_path="etna.series.blocks"
)


class SeriesBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=64)
    introduction = blocks.TextBlock(max_length=512)
    image = ImageChooserBlock(
        required=False,
        help_text="If image is not specified, an image set from the series taxonomy will be used.",
    )
    series = SeriesChooserBlock()
    show_only_digitised_records = blocks.BooleanBlock(default=True)

    class Meta:
        template = "series/blocks/series_block.html"
        help_text = "Promote a series of records."
        icon = "folder"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        series: Series = value["series"]

        if series is not None:
            context["series_url"] = get_series_search_results_url(
                series, only_digitised=value["show_only_digitised_records"]
            )
            context["category"] = series.get_category_display()
            context["image"] = value["image"] or series.image
        return context
