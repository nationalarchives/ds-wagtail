from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.ui.tables import Column, DateColumn, TitleColumn
from wagtail.admin.views.reports import ReportView
from wagtail.models import ReferenceIndex

from .models import CustomImage


class ImagesWithNoAltTextReportFilterSet(WagtailFilterSet):
    """
    Allow editors to filter by collection
    """

    class Meta:
        model = CustomImage
        fields = ["collection"]


class ImagesWithNoAltTextReport(ReportView):
    """
    Report showing all images that have no alt text (description is empty).
    """

    model = CustomImage
    index_url_name = "images_with_no_alt_text_report"
    index_results_url_name = "images_with_no_alt_text_report_results"
    header_icon = "image"
    page_title = "Images with no alt text"
    filterset_class = ImagesWithNoAltTextReportFilterSet
    list_export = ["id", "title", "collection", "usage_count", "created_at"]
    export_filename = "images_with_no_alt_text_report"
    columns = [
        TitleColumn(
            "title", label="Title", url_name="wagtailimages:edit", sort_key="title"
        ),
        Column("collection", label="Collection"),
        Column("usage_count", label="Usage count"),
        DateColumn("created_at", label="Created at", sort_key="created_at"),
    ]

    def get_queryset(self):
        # select_related avoids a query per row for the collection column, and
        # annotate avoids one for usage_count (both of which cause an N+1 query problem)
        return (
            super()
            .get_queryset()
            .filter(description="")
            .select_related("collection")
            .annotate(usage_count=ReferenceIndex.usage_count_subquery(CustomImage))
        )
