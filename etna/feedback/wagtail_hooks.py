from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from wagtail import hooks
from wagtail.admin.menu import AdminOnlyMenuItem

from etna.feedback.views import FeedbackSubmissionReportView


@hooks.register("register_admin_urls")
def register_feedback_repor_url():
    return [
        path(
            "reports/feedback-submissions/",
            FeedbackSubmissionReportView.as_view(),
            name="feedback_submission_report",
        ),
    ]


@hooks.register("register_reports_menu_item")
def register_feedback_report_menu_item():
    return AdminOnlyMenuItem(
        _("Feedback submissions"),
        reverse("feedback_submission_report"),
        classnames="icon icon-" + FeedbackSubmissionReportView.header_icon,
        order=700,
    )
