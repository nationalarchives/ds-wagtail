from django import forms
from django.core.exceptions import ValidationError
from django.db import models

from app.media.time_utils import (
    HHMMSS_PLACEHOLDER,
    duration_validation_message,
    normalise_hhmmss_for_display,
    parse_duration_input_to_seconds,
)

NON_NEGATIVE_DURATION_VALIDATION_MESSAGE = (
    "Duration must be greater than or equal to 0."
)


def is_negative(value):
    if isinstance(value, int):
        return value < 0

    if isinstance(value, str):
        stripped = value.strip()
        return stripped.startswith("-") and stripped[1:].isdigit()

    return False


class MediaDurationFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("help_text", "Enter duration as HH:MM:SS.")
        kwargs.setdefault(
            "widget",
            forms.TextInput(attrs={"placeholder": HHMMSS_PLACEHOLDER}),
        )
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        return normalise_hhmmss_for_display(value, parse_duration_input_to_seconds)

    def clean(self, value):
        data = super().clean(value)
        if data in self.empty_values:
            return None

        if is_negative(data):
            raise ValidationError(NON_NEGATIVE_DURATION_VALIDATION_MESSAGE)

        seconds = parse_duration_input_to_seconds(data)
        if seconds is None:
            raise ValidationError(duration_validation_message(data))

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

        if is_negative(value):
            raise ValidationError(NON_NEGATIVE_DURATION_VALIDATION_MESSAGE)

        seconds = parse_duration_input_to_seconds(value)
        if seconds is None:
            raise ValidationError(duration_validation_message(value))

        return int(seconds)

    def get_prep_value(self, value):
        if value in self.empty_values:
            return 0

        return self.to_python(value)

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", MediaDurationFormField)
        return models.Field.formfield(self, **kwargs)
