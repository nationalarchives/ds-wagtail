import logging
import uuid

from typing import Any, Dict, Optional

from django.contrib.contenttypes.models import ContentType
from django.forms import Form
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView

from wagtail.admin.auth import permission_denied
from wagtail.admin.views.reports import ReportView
from wagtail.models import Revision

from etna.feedback.forms import FeedbackForm
from etna.feedback.models import FeedbackPrompt, FeedbackSubmission

logger = logging.getLogger(__name__)


class VersionedFeedbackViewMixin:
    """
    Mixin for view classes that are initialized from a prompt_id/version
    combination, which determine options and messaging shown to the user.
    """

    def setup(
        self,
        request: HttpRequest,
        prompt_id: uuid.UUID,
        version: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().setup(request, **kwargs)
        self.prompt_id = prompt_id
        self.version = version
        self.is_ajax = request.POST.get("is_ajax", "false") == "true"
        if version:
            self.prompt_revision = get_object_or_404(
                Revision,
                content_type=ContentType.objects.get_for_model(FeedbackPrompt),
                id=version,
            )
            self.prompt = self.prompt_revision.as_object()
            if self.prompt.public_id != prompt_id:
                raise Http404("Bad prompt_id / version combination.")
        else:
            self.prompt = get_object_or_404(
                FeedbackPrompt.objects.all().select_related("latest_revision"),
                public_id=prompt_id,
            )
            self.prompt_revision = self.prompt.latest_revision


@method_decorator(csrf_exempt, name="dispatch")
class FeedbackSubmitView(VersionedFeedbackViewMixin, FormView):
    template_name = "feedback/submit.html"
    form_class = FeedbackForm

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        request = self.request
        kwargs.update(
            response_options=self.prompt.response_options,
            referer=request.META.get("HTTP_REFERER", ""),
            url_path_must_match_referer=request.resolver_match.namespace != "feedback",
        )
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(prompt=self.prompt, **kwargs)

    def form_valid(self, form: Form) -> HttpResponse:
        # Initialize submission
        obj = FeedbackSubmission(
            prompt=self.prompt,
            prompt_text=self.prompt.text,
            prompt_revision=self.prompt_revision,
        )

        # Set field values from form data
        for name, value in form.cleaned_data.items():
            setattr(obj, name, value)

        # Update fields from request data
        if self.request.user.is_authenticated:
            obj.user = self.request.user

        # Save submission to the DB
        obj.save()

        if self.is_ajax:
            return JsonResponse({"id": str(obj.public_id)})
        return self.redirect_on_success(
            obj.public_id, origin_url=form.cleaned_data["url"]
        )

    def form_invalid(self, form: Form) -> HttpResponse:
        # Log the failure
        logger.error(
            "Invalid feedback submission received",
            extra={"errors": form.errors.as_data(), "data": self.request.POST.lists()},
        )

        # Fake a successful response
        fake_id = uuid.uuid4()
        if self.is_ajax:
            return JsonResponse({"id": str(fake_id)})

        origin_url = form.cleaned_data["url"] if "url" not in form.errors else "/"
        return self.redirect_on_success(fake_id, origin_url)

    def get_success_url(self) -> str:
        return reverse(
            "feedback:success",
            kwargs={"prompt_id": self.prompt_id, "version": self.version},
        )

    def redirect_on_success(
        self, submission_id: uuid.UUID, origin_url: str
    ) -> HttpResponseRedirect:
        url = self.get_success_url()
        querystring = urlencode({"submission": submission_id, "next": origin_url})
        return HttpResponseRedirect(url + "?" + querystring)


class FeedbackSuccessView(VersionedFeedbackViewMixin, TemplateView):
    template_name = "feedback/success.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        try:
            submission_id = str(uuid.UUID(self.request.GET["submission"]))
        except (KeyError, ValueError):
            submission_id = None
        return super().get_context_data(
            prompt=self.prompt,
            next_url=self.request.GET.get("next", "/"),
            submission_id=submission_id,
            **kwargs,
        )


class FeedbackSubmissionReportView(ReportView):
    title = "Feedback submissions"
    header_icon = "form"
    model = FeedbackSubmission
    is_searchable = False
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
