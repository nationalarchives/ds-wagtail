from django import forms
from wagtail.images.forms import BaseImageForm


class CustomImageAdminForm(BaseImageForm):
    """
    Custom form for the Wagtail admin interface to handle the alternative_format field, to provide the "accept" attribute for the file input, allowing only specified file types to be selected in the file dialog.
    """

    class Meta(BaseImageForm.Meta):
        widgets = {
            **BaseImageForm.Meta.widgets,
            "alternative_format": forms.ClearableFileInput(
                attrs={"accept": ".csv,.xlsx,.xls"}
            ),
        }
