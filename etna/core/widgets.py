from django import forms
from django.utils.translation import gettext_lazy as _

from wagtail.admin.staticfiles import versioned_static
from wagtail.telepath import register
from wagtail.widget_adapters import WidgetAdapter


class LabelWidgetMixin:
    """
    A mixin that can be applied to any widget class to require it
    to have its own label. Great for sub-widgets!
    """

    def __init__(self, label: str, *args, **kwargs):
        self.label = label
        super().__init__(*args, **kwargs)


class TextInputWithLabel(LabelWidgetMixin, forms.TextInput):
    """
    A version of Django's basic TextInput widget that requires the
    input to have its own label.
    """

    pass


class DateInputWidget(forms.MultiWidget):
    """
    Copied from crispy-forms-gds, but changed to use better sub-widgets with label support
    and extra HTML attributes.

    The original definition can be found at:
    https://github.com/wildfish/crispy-forms-gds/blob/master/src/crispy_forms_gds/widgets.py
    """

    template_name = "widgets/date.html"

    def __init__(self, *args, **kwargs):
        widgets = [
            TextInputWithLabel(
                _("Day"),
                attrs={
                    "size": 2,
                    "placeholder": "DD",
                    "inputmode": "numeric",
                },
            ),
            TextInputWithLabel(
                _("Month"),
                attrs={
                    "size": 2,
                    "placeholder": "MM",
                    "inputmode": "numeric",
                },
            ),
            TextInputWithLabel(
                _("Year"),
                attrs={
                    "size": 4,
                    "placeholder": "YYYY",
                    "inputmode": "numeric",
                },
            ),
        ]
        super().__init__(widgets, **kwargs)

    def decompress(self, value):
        """
        Convert a ``date`` into values for the day, month and year so it can be
        displayed in the widget's fields.

        Args:
            value (date): the date to be displayed

        Returns:
            a 3-tuple containing the day, month and year components of the date.

        """
        if value:
            return value.day, value.month, value.year
        return None, None, None


class TextAreaWithCharacterCount(forms.Textarea):

    def media(self):
        media = forms.Media(
            js=[
                "admin/js/textarea-with-character-count.js",
            ],
            css={"all": [versioned_static("wagtailadmin/css/panels/draftail.css")]},
        )
        return media


class TextAreaWithCharacterCountAdapter(WidgetAdapter):
    js_constructor = "etna.core.widgets.TextAreaWithCharacterCount"

    def js_args(self, widget):
        return [
            widget.options,
        ]


register(TextAreaWithCharacterCountAdapter(), TextAreaWithCharacterCount)
