import re

from typing import Dict, List, Tuple, Union

from django import forms
from django.core.validators import MinLengthValidator
from django.utils.functional import cached_property

from ..ciim.client import SortBy, SortOrder
from ..ciim.constants import COLLECTION_CHOICES, LEVEL_CHOICES


class DynamicMultipleChoiceField(forms.MultipleChoiceField):
    """MultipleChoiceField whose choices can be updated to reflect API response data."""

    def valid_value(self, value):
        """Disable validation if the field choices are not yet set."""
        if not self.choices:
            return True
        return super().valid_value(value)

    @cached_property
    def config_choice_labels(self):
        return {value: label for value, label in self.choices}

    def choice_label_from_api_data(self, data: Dict[str, Union[str, int]]) -> str:
        count = f"{data['doc_count']:,}"
        # Firstly, use a label from the config choice values, if available
        try:
            return f"{self.config_choice_labels[data['key']]} ({count})"
        except KeyError:
            pass
        # Secondly, look for a 'label' value in the data provided by the API
        try:
            return f"{data['label']} ({count})"
        except KeyError:
            pass
        # Fall back to using the key value (which is the same in most cases)
        return f"{data['key']} ({count})"

    def update_choices(
        self, data: List[Dict[str, Union[str, int]]], order_alphabetically: bool = True
    ):
        """Populate choice list with aggregation data from the API.

        Expected ``data`` format:
        [
            {
                "key": "item",
                "doc_count": 10
            },
            …
        ]
        """
        choices = [
            (item["key"], self.choice_label_from_api_data(item)) for item in data
        ]
        if order_alphabetically:
            choices.sort(key=lambda x: x[1])
        self.choices = choices
        self.choices_updated = True


class FeaturedSearchForm(forms.Form):
    q = forms.CharField(
        label="Search here",
        # If no query is provided, pass None to client to fetch all results.
        empty_value=None,
        required=False,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(attrs={"class": "search-results-hero__form-search-box"}),
    )


class BaseCollectionSearchForm(forms.Form):
    """
    NOTE: For dynamic fields (where choices are update from the API result), the field
    name should be a lower-case/underscored version of the API filter name (which are
    typically in in 'camelCase'). For example:

    "fieldname" -> "fieldname"
    "fieldName" -> "field_name"
    """

    # Fields who's choices are updated to reflect the API response
    dynamic_choice_fields = (
        "collection",
        "level",
        "topic",
        "closure",
        "catalogue_source",
    )

    q = forms.CharField(
        label="Search term",
        # If no query is provided, pass None to client to fetch all results.
        empty_value=None,
        required=False,
        widget=forms.TextInput(attrs={"class": "search-results-hero__form-search-box"}),
    )
    group = forms.ChoiceField(
        label="bucket",
        choices=[],
    )
    filter_keyword = forms.CharField(
        label="Search within",
        # If no filter_keyword is provided, pass None to client bypass search within
        empty_value=None,
        required=False,
        widget=forms.TextInput(attrs={"class": "search-filters__search"}),
    )
    level = DynamicMultipleChoiceField(
        label="Level",
        choices=LEVEL_CHOICES,
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"},
        ),
        required=False,
    )
    topic = DynamicMultipleChoiceField(
        label="Topics",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    collection = DynamicMultipleChoiceField(
        label="Collection",
        choices=COLLECTION_CHOICES,
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    closure = DynamicMultipleChoiceField(
        label="Closure Status",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    catalogue_source = DynamicMultipleChoiceField(
        label="Catalogue Sources",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    opening_start_date = forms.DateTimeField(
        label="From",
        widget=forms.DateTimeInput(
            attrs={"type": "input", "placeholder": "YYYY-MM-DD"}
        ),
        required=False,
    )
    opening_end_date = forms.DateTimeField(
        label="To",
        widget=forms.DateTimeInput(
            attrs={"type": "input", "placeholder": "YYYY-MM-DD"}
        ),
        required=False,
    )
    sort_by = forms.ChoiceField(
        label="Sort by",
        choices=[
            (SortBy.RELEVANCE.value, "Relevance"),
            (SortBy.DATE_OPENING.value, "Date"),
            (SortBy.TITLE.value, "Title"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "search-sort-view__form-select"}),
    )
    sort_order = forms.ChoiceField(
        label="Sort order",
        choices=[
            (SortOrder.ASC.value, "Ascending"),
            (SortOrder.DESC.value, "Descending"),
        ],
        required=False,
    )
    display = forms.ChoiceField(
        choices=[
            ("grid", "Grid"),
            ("list", "List"),
        ],
        required=False,
    )

    def clean(self):
        """Collect selected filters to pass to the client in view."""
        cleaned_data = super().clean()

        try:
            if cleaned_data.get("opening_start_date") > cleaned_data.get(
                "opening_end_date"
            ):
                self.add_error(
                    "opening_start_date", "Start date cannot be after end date"
                )
        except TypeError:
            # Either one or both date fields are empty. No further validation necessary.
            ...

        return cleaned_data

    @cached_property
    def selected_filters(self) -> Dict[str, List[Tuple[str, str]]]:
        """List of selected values, keyed by the corresponding field name.

        Used by template to output a list of selected filters.

        Method must be called on a bound form (post validation)

        TODO: When we inevitably shift to class-based views, this logic
        should be moved to the view.
        """
        return_value = {
            field_name: self.cleaned_data.get(field_name)
            for field_name in self.dynamic_choice_fields
        }

        # Remove items with no values
        return_value = {k: v for k, v in return_value.items() if v}

        # Replace raw values with (key, label) tuples
        for field_name, selected_options in return_value.items():
            for value, label in self.fields[key].choices:
                if value in values:
                    label_without_count = re.sub(r" \([0-9\,]+\)", "", label, 0)
                    values.remove(value)
                    values.append((value, label_without_count))

        # Remove values that do not match choices
        for value in return_value.values():
            for i, item in enumerate(value):
                if isinstance(item, str):
                    value.pop(i)

        return return_value


class CatalogueSearchForm(BaseCollectionSearchForm):
    group = forms.ChoiceField(
        label="bucket",
        choices=[
            ("group:tna", "TNA"),
            ("group:nonTna", "NonTNA"),
            ("group:creator", "Creator"),
            ("group:archive", "Archive"),
            ("group:digitised", "Digitised"),
        ],
    )


class WebsiteSearchForm(BaseCollectionSearchForm):
    group = forms.ChoiceField(
        label="bucket",
        choices=[
            ("group:blog", "Blog"),
            ("group:image", "Image"),
            ("group:researchGuide", "Research Guide"),
            ("group:audio", "Audio"),
            ("group:video", "Video"),
            ("group:insight", "Insights"),
            ("group:highlight", "Highlights"),
        ],
    )
