import logging

from django.utils.translation import gettext_lazy as _

from wagtail.admin.auth import permission_denied
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.views.reports import ReportView
from wagtail.admin.widgets import AdminDateInput

import django_filters

from etna.feedback.constants import SentimentChoices
from etna.feedback.models import FeedbackSubmission

logger = logging.getLogger(__name__)

__all__ = [
    "FeedbackSubmissionReportView",
]


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


class FeedbackSubmissionReportView(ReportView):
    title = "Feedback submissions"
    header_icon = "form"
    model = FeedbackSubmission
    is_searchable = False
    filterset_class = FeedbackSubmissionFilterSet
    template_name = "feedback/reports/submission_report.html"

    list_display = [
        "received_at",
        "path",
        "prompt_text",
        "response",
        "comment_truncated",
    ]
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

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return permission_denied(request)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["table"].base_url = self.request.path
        return context
