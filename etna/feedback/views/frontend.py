import logging
import uuid
from http import HTTPStatus
from typing import Any, Dict

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
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
from wagtail.models import Revision

from etna.feedback.forms import FeedbackCommentForm, FeedbackForm
from etna.feedback.models import FeedbackPrompt, FeedbackSubmission
from etna.feedback.utils import sign_submission_id

logger = logging.getLogger(__name__)


__all__ = [
    "FeedbackSubmitView",
    "FeedbackSuccessView",
    "FeedbackCommentSubmitView",
    "FeedbackCommentSuccessView",
]


class VersionedFeedbackViewMixin:
    """
    Mixin for view classes that are initialized from a prompt_id/version
    combination, which determine options and messaging shown to the user.
    """

    def setup(
        self,
        request: HttpRequest,
        prompt_id: uuid.UUID,
        version: int,
        **kwargs,
    ) -> None:
        super().setup(request, **kwargs)
        self.prompt_id = prompt_id
        self.version = version
        self.is_ajax = request.POST.get("is_ajax", "false") == "true"
        self.prompt_revision = get_object_or_404(
            Revision,
            content_type=ContentType.objects.get_for_model(FeedbackPrompt),
            id=version,
        )
        self.prompt = self.prompt_revision.as_object()
        if self.prompt.public_id != prompt_id:
            raise Http404("Bad prompt_id / version combination.")


@method_decorator(csrf_exempt, name="dispatch")
class FeedbackSubmitView(VersionedFeedbackViewMixin, FormView):
    """
    A view for vaidating and storing feedback submitted from a prompt.

    The URL includes `prompt_id` and `version` parameters, which are used to
    to determine the exact version of the prompt seen by the user, and the
    response options that were available to them.

    NOTE: This view only responds to POST requests.
    """

    form_class = FeedbackForm
    http_method_names = ["post"]

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update(
            response_options=self.prompt.response_options,
            response_label=self.prompt.text,
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
            return JsonResponse(
                {
                    "id": str(obj.public_id),
                    "signature": sign_submission_id(obj.public_id),
                    "comment_prompt_text": form.cleaned_data["comment_prompt_text"],
                }
            )

        querystring = urlencode(
            {"submission": obj.public_id, "next": form.cleaned_data["url"]}
        )
        return HttpResponseRedirect(self.get_success_url() + "?" + querystring)

    def form_invalid(self, form: Form) -> HttpResponse:
        data = {
            "success": False,
            "form_data": dict(form.data),
            "errors": dict(form.errors),
        }
        return JsonResponse(data=data, status=HTTPStatus.BAD_REQUEST)

    def get_success_url(self) -> str:
        return reverse(
            "feedback:success",
            kwargs={"prompt_id": self.prompt_id, "version": self.version},
        )


class FeedbackSuccessView(VersionedFeedbackViewMixin, TemplateView):
    template_name = "feedback/success.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        comment_form = None
        try:
            submission = FeedbackSubmission.objects.get(
                public_id=self.request.GET["submission"]
            )
        except (KeyError, ValidationError, FeedbackSubmission.DoesNotExist):
            pass
        else:
            if submission.comment_prompt_text and not submission.comment:
                comment_form = FeedbackCommentForm(
                    prompt_text=submission.comment_prompt_text,
                    initial={
                        "submission": submission.public_id,
                        "signature": sign_submission_id(submission.public_id),
                    },
                )

        return super().get_context_data(
            prompt=self.prompt,
            next_url=self.request.GET.get("next", "/"),
            comment_form=comment_form,
            **kwargs,
        )


@method_decorator(csrf_exempt, name="dispatch")
class FeedbackCommentSubmitView(VersionedFeedbackViewMixin, FormView):
    """A view for validating and saving comments submitted to accompany feedback.

    The URL includes `prompt_id` and `version` parameters, which are used to
    to determine the exact version of the prompt seen by the user.

    NOTE: This view only responds to POST requests.
    """

    form_class = FeedbackCommentForm
    http_method_names = ["post"]

    def form_valid(self, form: Form) -> HttpResponse:
        obj = form.cleaned_data["submission"]
        if form.cleaned_data["comment"]:
            obj.comment = form.cleaned_data["comment"]
            obj.save(update_fields=["comment"])
        if self.is_ajax:
            return JsonResponse({"success": True})
        querystring = urlencode({"next": obj.full_url})
        return HttpResponseRedirect(self.get_success_url() + "?" + querystring)

    def form_invalid(self, form):
        data = {
            "success": False,
            "form_data": dict(form.data),
            "errors": dict(form.errors),
        }
        return JsonResponse(data=data, status=HTTPStatus.BAD_REQUEST)

    def get_success_url(self) -> str:
        return reverse(
            "feedback:comment_success",
            kwargs={"prompt_id": self.prompt_id, "version": self.version},
        )


class FeedbackCommentSuccessView(VersionedFeedbackViewMixin, TemplateView):
    template_name = "feedback/success.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(
            prompt=self.prompt,
            next_url=self.request.GET.get("next", "/"),
            **kwargs,
        )
