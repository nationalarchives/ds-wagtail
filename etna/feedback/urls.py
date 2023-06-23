from django.urls import path

from etna.feedback import views

app_name = "feedback"
urlpatterns = [
    path(
        "submit/<uuid:prompt_id>/<int:version>/",
        views.FeedbackSubmitView.as_view(),
        name="submit",
    ),
    path(
        "submit/comment/",
        views.FeedbackCommentSubmitView.as_view(),
        name="submit_comment",
    ),
    path(
        "submit/<uuid:prompt_id>/<int:version>/success/",
        views.FeedbackSuccessView.as_view(),
        name="success",
    ),
]
