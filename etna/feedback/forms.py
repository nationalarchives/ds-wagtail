import hmac
import uuid

from typing import Optional, Union
from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError
from django.http.request import QueryDict, validate_host

from wagtail.blocks import StreamValue
from wagtail.models import Page, Revision, Site
from wagtail.models.sites import get_site_for_hostname

import nh3

from etna.feedback import constants
from etna.feedback.models import FeedbackSubmission
from etna.feedback.utils import get_allowed_hosts, normalize_path, sign_submission_id
from etna.feedback.widgets import ResponseSubmitButtonList


class FeedbackForm(forms.Form):
    response = forms.TypedChoiceField(coerce=uuid.UUID, choices=())
    url = forms.URLField(widget=forms.HiddenInput)
    page = forms.ModelChoiceField(
        Page.objects.all(), required=False, widget=forms.HiddenInput
    )
    page_revision = forms.ModelChoiceField(
        Revision.objects.all(), required=False, widget=forms.HiddenInput
    )
    page_type = forms.CharField(required=False, widget=forms.HiddenInput)
    page_title = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(
        self,
        *args,
        response_options: StreamValue,
        response_label: str,
        **kwargs,
    ) -> None:
        """
        Overrides Form.__init__() to accept additional inputs relevant to this form:

        `response_label`:
            The `text` field value from the `FeedbackPRompt` instance this form is
            being used to represent.

        `response_options`:
            The `response_options` field value from the `FeedbackPrompt` instance this form
            is being used to represent. The value is used to generate a custom choice widget
            for the `response` field, and is also used for validation.
        """
        self.response_options = response_options
        super().__init__(*args, **kwargs)
        widget = ResponseSubmitButtonList(response_options)
        self.fields["response"].label = response_label
        self.fields["response"].widget = widget
        self.fields["response"].choices = widget.choices

    def clean_url(self) -> Union[str, None]:
        value = self.cleaned_data.get("url")
        if value is None:
            return None

        try:
            parse_result = urlparse(value)
        except ValueError:
            raise ValidationError("value is not a valid URL.", code="invalid")

        if not validate_host(parse_result.hostname, get_allowed_hosts()):
            raise ValidationError("url hostname is invalid.", code="invalid")

        # Find the relevant Site
        try:
            site = get_site_for_hostname(parse_result.hostname, parse_result.port)
        except Site.DoesNotExist:
            raise ValidationError(
                "value could not be matched to a Wagtail site.",
                code="invalid",
            )

        # Create dict from querystring data
        query_params = {
            name: values for name, values in QueryDict(parse_result.query).lists()
        }

        # Add derived values to 'cleaned_data'
        self.cleaned_data.update(
            full_url=value,
            site=site,
            path=normalize_path(parse_result.path),
            query_params=query_params,
        )

        return value

    def clean_response(self) -> Union[uuid.UUID, None]:
        value = self.cleaned_data.get("response")
        if value is None:
            return None

        # Add derived values to 'cleaned_data'
        for option in self.response_options:
            if str(option.id) == str(value):
                self.cleaned_data.update(
                    response_label=option.value["label"],
                    response_sentiment=option.value["sentiment"],
                    comment_prompt_text=option.value["comment_prompt_text"],
                )
                break

        return value

    def clean_page_revision(self) -> Optional[Revision]:
        revision = self.cleaned_data.get("page_revision")
        page = self.cleaned_data.get("page")

        if not page and not revision:
            return None  # Nothing to validate

        # Validate the value
        if page and not revision:
            raise ValidationError(
                "this field is required when 'page' is provided.", code="required"
            )
        if revision and not page:
            raise ValidationError(
                "this field should only be provided when 'page' is also provided.",
                code="unexpected",
            )

        if (
            revision.content_type != page.content_type
            or int(revision.object_id) != page.pk
        ):
            raise ValidationError(
                "the specified revision does not match the specified 'page'.",
                code="mismatch",
            )

        # When valid, add 'page_revision_published' to cleaned_data
        self.cleaned_data["page_revision_published"] = page.last_published_at

        return revision


class FeedbackCommentForm(forms.Form):
    submission = forms.ModelChoiceField(
        queryset=FeedbackSubmission.objects.filter(comment=""),
        widget=forms.HiddenInput(),
        to_field_name="public_id",
    )
    signature = forms.CharField(widget=forms.HiddenInput())
    comment = forms.CharField(
        label=constants.DEFAULT_COMMENT_PROMPT_TEXT,
        required=False,
        widget=forms.Textarea({"cols": 40, "rows": 5}),
    )

    def __init__(self, *args, prompt_text: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if prompt_text:
            self.fields["comment"].label = prompt_text

    def clean_comment(self) -> str:
        # Strip HTML from all comment submissions
        value = self.cleaned_data.get("comment")
        if value is None:
            return ""
        return nh3.clean(value)

    def clean(self) -> str:
        # Validate the 'signature' value against the 'id' value
        data = super().clean()
        submission = data.get("submission")
        signature = data.get("signature")

        if (
            submission
            and signature
            and not hmac.compare_digest(
                sign_submission_id(submission.public_id), signature
            )
        ):
            self.add_error(
                "signature",
                ValidationError(
                    "Value does not match the specified submission.", code="invalid"
                ),
            )
        return data
