from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.ui.tables import Column, DateColumn, TitleColumn
from wagtail.admin.views.reports import ReportView

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
        queryset = CustomImage.objects.filter(description="")

        ordering = self.request.GET.get("ordering")

        if ordering in ["title", "-title", "created_at", "-created_at"]:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset
