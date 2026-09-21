from wagtail.admin.ui.tables import Column, TitleColumn
from wagtail.admin.views.reports import ReportView

from .models import CustomImage


class ImagesWithNoAltTextReport(ReportView):
    index_url_name = "images_with_no_alt_text_report"
    index_results_url_name = "images_with_no_alt_text_report_results"
    header_icon = "image"
    page_title = "Images with no alt text"
    columns = [
        TitleColumn(
            "title", label="Title", url_name="wagtailimages:edit", sort_key="title"
        ),
        Column("collection", label="Collection"),
        Column("usage_count", label="Usage count"),
        Column("created_at", label="Created at"),
    ]

    def get_queryset(self):
        return CustomImage.objects.filter(description="")
