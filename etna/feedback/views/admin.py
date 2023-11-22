import logging

from django.utils.translation import gettext_lazy as _

from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.widgets import AdminDateInput
from wagtail.snippets.views.snippets import SnippetViewSet, TitleColumn

import django_filters

from etna.feedback.constants import SentimentChoices
from etna.feedback.models import FeedbackSubmission

logger = logging.getLogger(__name__)

__all__ = [
    "FeedbackSubmissionViewSet",
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


class FeedbackSubmissionViewSet(SnippetViewSet):
    add_to_admin_menu = True
    menu_label = _("Feedback")
    model = FeedbackSubmission
    icon = "form"
    index_template_name = "feedback/admin/feedbacksubmission_index.html"
    filterset_class = FeedbackSubmissionFilterSet

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
        "page_type",
        "page_title",
        "page_revision_id",
        "page_revision_published",
        "user_id",
        "site_id",
    ]

    list_display = [
        # url related methods are deliberately omitted here to prevent rendering of an edit link
        # (which Wagtail does regardless of user permissions)
        TitleColumn("id", label=_("ID")),
        "received_at",
        "path",
        "prompt_text",
        "response",
        "comment_truncated",
    ]
