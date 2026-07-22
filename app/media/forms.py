from django import forms
from django.core.exceptions import ValidationError
from wagtailmedia.forms import BaseMediaForm

from app.media.time_utils import (
    DURATION_VALIDATION_MESSAGE,
    HHMMSS_PLACEHOLDER,
    normalise_hhmmss_for_display,
    parse_media_duration_to_seconds,
)


class MediaDurationField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("help_text", "Enter duration as HH:MM:SS.")
        kwargs.setdefault(
            "widget",
            forms.TextInput(attrs={"placeholder": HHMMSS_PLACEHOLDER}),
        )
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        return normalise_hhmmss_for_display(value, parse_media_duration_to_seconds)

    def clean(self, value):
        data = super().clean(value)
        if data in self.empty_values:
            return None

        seconds = parse_media_duration_to_seconds(data)
        if seconds is None:
            raise ValidationError(DURATION_VALIDATION_MESSAGE)

        return seconds


class EtnaMediaBaseForm(BaseMediaForm):
    duration = MediaDurationField(required=False)
