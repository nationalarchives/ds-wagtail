from typing import List, Tuple

from django import forms
from django.utils.translation import gettext_lazy as _

from etna.ciim.exceptions import KongAPIError
from etna.records.api import records_client

from .models import Highlight


class HighlightCreateStep1Form(forms.Form):
    record_reference = forms.CharField(
        label=_("Record reference"),
        help_text=_("The reference for the record you want to create a highlight for."),
    )
    teaser_image = forms.ImageField(
        label=_("Teaser image"),
        required=False,
        help_text=_(
            "An optional image to use in places where this highlight is featured in "
            "content. If you do not have an image, or want to choose an existing "
            "one from Wagtail's image library, leave this blank for now (it can be "
            "added later)."
        ),
    )
    step = forms.IntegerField(initial=1, widget=forms.HiddenInput())

    def clean_record_reference(self):
        record_reference = self.cleaned_data["record_reference"]
        try:
            search_result = records_client.search(q=record_reference, size=20)
        except KongAPIError:
            raise forms.ValidationError(
                _("There was an error contacting CIIM. Please try again later."),
                code="ciim_comms_error",
            )
        hits = [r for r in search_result]
        if not hits:
            raise forms.ValidationError(
                _("No records were found matching this reference."),
                code="invalid_record_reference",
            )
        self.cleaned_data["record_best_match"] = hits[0]
        self.cleaned_data["record_matches"] = hits


class HighlightCreateStep2Form(forms.ModelForm):
    record = forms.CharField(label=_("Which record did you mean?"), required=True)
    step = forms.IntegerField(initial=2, widget=forms.HiddenInput())

    class Meta:
        model = Highlight
        fields = ["record", "title", "dates", "description", "alt_text", "teaser_image"]
        widgets = {
            "teaser_image": forms.HiddenInput(),
        }

    def __init__(self, *args, record_choices: List[Tuple[str, str]] = [], **kwargs):
        super().__init__(*args, **kwargs)

        record_field = self.fields["record"]
        if len(record_choices) > 1:
            # Allow disambiguation between multiple matching records
            record_field.widget = forms.RadioSelect(choices=record_choices)
        else:
            # If there is only a single matching record, or we're handling a posted
            # form without the choices being supplied, hide the field
            record_field.widget = forms.HiddenInput()

        if not self.initial.get("teaser_image"):
            self.fields["alt_text"].required = False
