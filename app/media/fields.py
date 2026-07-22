from django import forms
from django.core.exceptions import ValidationError
from django.db import models

from app.media.time_utils import (
    DURATION_VALIDATION_MESSAGE,
    HHMMSS_PLACEHOLDER,
    normalise_hhmmss_for_display,
    parse_media_duration_to_seconds,
)


class MediaDurationFormField(forms.CharField):
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


class MediaDurationField(models.PositiveIntegerField):
    description = "Media duration stored as seconds"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("blank", True)
        kwargs.setdefault("default", 0)
        kwargs.setdefault("help_text", "Enter duration as HH:MM:SS.")
        kwargs.setdefault("verbose_name", "duration")
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None

        seconds = parse_media_duration_to_seconds(value)
        if seconds is None:
            raise ValidationError(DURATION_VALIDATION_MESSAGE)

        return int(seconds)

    def get_prep_value(self, value):
        if value in self.empty_values:
            return 0

        return self.to_python(value)

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", MediaDurationFormField)
        return super().formfield(**kwargs)
