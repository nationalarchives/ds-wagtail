from django import forms
from django.core.exceptions import ValidationError
from django.db import models

from app.media.time_utils import (
    DURATION_VALIDATION_MESSAGE,
    HHMMSS_PLACEHOLDER,
    normalise_hhmmss_for_display,
    parse_media_duration_to_seconds,
)

NON_NEGATIVE_DURATION_VALIDATION_MESSAGE = (
    "Duration must be greater than or equal to 0."
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

        if isinstance(data, str):
            data_stripped = data.strip()
            if data_stripped.startswith("-") and data_stripped[1:].isdigit():
                raise ValidationError(NON_NEGATIVE_DURATION_VALIDATION_MESSAGE)

        seconds = parse_media_duration_to_seconds(data)
        if seconds is None:
            raise ValidationError(DURATION_VALIDATION_MESSAGE)
        if seconds < 0:
            raise ValidationError(NON_NEGATIVE_DURATION_VALIDATION_MESSAGE)

        return seconds


class MediaDurationField(models.IntegerField):
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

        if isinstance(value, int) and value < 0:
            raise ValidationError(NON_NEGATIVE_DURATION_VALIDATION_MESSAGE)
        if isinstance(value, str):
            value_stripped = value.strip()
            if value_stripped.startswith("-") and value_stripped[1:].isdigit():
                raise ValidationError(NON_NEGATIVE_DURATION_VALIDATION_MESSAGE)

        seconds = parse_media_duration_to_seconds(value)
        if seconds is None:
            raise ValidationError(DURATION_VALIDATION_MESSAGE)
        if seconds < 0:
            raise ValidationError(NON_NEGATIVE_DURATION_VALIDATION_MESSAGE)

        return int(seconds)

    def get_prep_value(self, value):
        if value in self.empty_values:
            return 0

        return self.to_python(value)

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", MediaDurationFormField)
        return models.Field.formfield(self, **kwargs)
