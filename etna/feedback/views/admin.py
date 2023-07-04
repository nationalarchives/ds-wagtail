import logging

from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.views.mixins import SpreadsheetExportMixin
from wagtail.admin.widgets import AdminDateInput
from wagtail.snippets.views.snippets import (
    IndexView,
    SnippetTitleColumn,
    SnippetViewSet,
)

import django_filters

from etna.feedback.constants import SentimentChoices
from etna.feedback.models import FeedbackSubmission

logger = logging.getLogger(__name__)

__all__ = [
    "FeedbackSubmissionViewSet",
]


class FeedbackSubmissionIndexView(SpreadsheetExportMixin, IndexView):
    """
    A customised version of `wagtail.snippets.views.snippets.IndexView`
    that supports exporting as CSV or XLSX
    """

    # Columns to include in the export
    list_export = [
        "id",
        "public_id",
        "received_at",
        "full_url",
        "path",
        "query_params",
        "prompt_text",
        "response_label",
        "response_sentiment",
        "sentiment_label",
        "comment_prompt_text",
        "comment",
        "prompt_id",
        "prompt_revision_id",
        "page_id",
        "page_revision_id",
        "page_revision_published",
        "user_id",
        "site_id",
    ]

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.is_export = request.GET.get("export") in self.FORMATS
        if self.is_export:
            self.paginate_by = None
            self.filters, self.object_list = self.filter_queryset(self.get_queryset())
            return self.as_spreadsheet(self.object_list, request.GET.get("export"))
        return super().get(request, *args, **kwargs)


class FeedbackSubmissionFilterSet(WagtailFilterSet):
    received_from = django_filters.DateFilter(
        field_name="received_at",
        lookup_expr="date__gte",
        label=_("Date received (from)"),
        widget=AdminDateInput,
    )
    received_to = django_filters.DateFilter(
        field_name="received_at",
        lookup_expr="date__lte",
        label=_("Date received (to)"),
        widget=AdminDateInput,
    )
    response_sentiment = django_filters.ChoiceFilter(
        choices=SentimentChoices.choices, label=_("Sentiment")
    )

    class Meta:
        model = FeedbackSubmission
        fields = {
            "path": ["iexact", "istartswith"],
        }


class FeedbackSubmissionViewSet(SnippetViewSet):
    model = FeedbackSubmission
    icon = "form"
    index_view_class = FeedbackSubmissionIndexView
    index_template_name = "feedback/admin/feedbacksubmission_index.html"
    filterset_class = FeedbackSubmissionFilterSet

    list_display = [
        # url related methods are deliberately omitted here to prevent rendering of an edit link
        # (which Wagtail does regardless of user permissions)
        SnippetTitleColumn("received_at"),
        "path",
        "prompt_text",
        "response",
        "comment_truncated",
    ]
