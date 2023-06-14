import math
import uuid

from typing import Optional, Union
from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError
from django.http.request import QueryDict, validate_host
from django.utils.translation import gettext_lazy as _

from wagtail.blocks import StreamValue
from wagtail.models import Page, Revision, Site
from wagtail.models.sites import get_site_for_hostname

import bleach

from etna.feedback import constants
from etna.feedback.utils import get_allowed_hosts, normalize_path
from etna.feedback.widgets import FeedbackResponseSelect


class FeedbackForm(forms.Form):
    response = forms.TypedChoiceField(
        coerce=uuid.UUID, label=_("Your response"), choices=()
    )
    comment = forms.CharField(
        label=_("Comment (optional)"),
        help_text=f"Length limit: {constants.COMMENT_MAX_LENGTH} characters.",
        max_length=constants.COMMENT_MAX_LENGTH,
        required=False,
        widget=forms.Textarea(
            {
                "cols": math.floor(constants.COMMENT_MAX_LENGTH / 5),
                "rows": 5,
                "maxlength": constants.COMMENT_MAX_LENGTH,
            }
        ),
    )
    url = forms.URLField(widget=forms.HiddenInput)
    page = forms.ModelChoiceField(
        Page.objects.all(), required=False, widget=forms.HiddenInput
    )
    page_revision = forms.ModelChoiceField(
        Revision.objects.all(), required=False, widget=forms.HiddenInput
    )

    def __init__(
        self,
        response_options: StreamValue,
        *args,
        referer: Optional[str] = None,
        url_path_must_match_referer: Optional[bool] = True,
        **kwargs,
    ) -> None:
        """
        Overrides Form.__init__() to accept additional inputs relevant to this form:

        `response_options`:
            The `response_options` field value from the `FeedbackPrompt` instance this form
            is being used to represent. The value is used to generate a custom choice widget
            for the `response` field, and is also used for validation.

        `referer`:
            The `Referer` header value from the current request. When `url_path_must_match_referer`
            is `True`, validation of `url` will fail if the 'path' differs to this one.

        `url_path_must_match_referer`:
            Determines whether the `url` value is validated against the `referer` path.

        """
        self.response_options = response_options
        self.referer = referer
        self.url_path_must_match_referer = url_path_must_match_referer

        super().__init__(*args, **kwargs)
        widget = FeedbackResponseSelect(response_options)
        self.fields["response"].widget = widget
        self.fields["response"].choices = widget.choices

    def clean_url(self) -> Union[str, None]:
        allowed_hosts = get_allowed_hosts()

        value = self.cleaned_data.get("url")
        if value is None:
            return None

        try:
            parse_result = urlparse(value)
        except ValueError:
            raise ValidationError("value is not a valid URL.", code="invalid")

        if not validate_host(parse_result.hostname, allowed_hosts):
            raise ValidationError("url hostname is invalid.", code="invalid")

        try:
            referer_parse_result = urlparse(self.referer)
        except ValueError:
            raise ValidationError("referer is not at a valid URL.", code="invalid")

        if not validate_host(referer_parse_result.hostname, allowed_hosts):
            raise ValidationError("referer hostname is invalid.", code="invalid")

        if (
            self.url_path_must_match_referer
            and parse_result.path != referer_parse_result.path
        ):
            raise ValidationError(
                f"path '{parse_result.path}' differs from '{referer_parse_result.path}'.",
                code="invalid",
            )

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
                )
                break

        return value

    def clean_comment(self) -> str:
        try:
            raw = self.cleaned_data["comment"]
        except KeyError:
            return ""
        return bleach.clean(raw, tags=[], strip=True)

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
