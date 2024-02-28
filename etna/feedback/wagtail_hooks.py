from etna.feedback.models import FeedbackSubmission
from etna.feedback.views import FeedbackSubmissionViewSet
from wagtail import hooks
from wagtail.snippets.models import register_snippet


@hooks.register("construct_snippet_listing_buttons")
def remove_edit_button_for_submissions(buttons, snippet, user):
    if isinstance(snippet, FeedbackSubmission):
        buttons[:] = [item for item in buttons if item.label != "Edit"]


register_snippet(FeedbackSubmission, viewset=FeedbackSubmissionViewSet)
