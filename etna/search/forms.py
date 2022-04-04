from typing import Dict, List, Union
from django import forms
from django.core.validators import MinLengthValidator
from django.utils.functional import cached_property

from ..ciim.client import SortBy, SortOrder


class DynamicMultipleChoiceField(forms.MultipleChoiceField):
    """MultipleChoiceField whose choices can be updated to reflect API response data."""

    def valid_value(self, value):
        """Disable validation if the field choices are not yet set."""
        if not self.choices:
            return True
        return super().valid_value(value)

    @cached_property
    def original_choice_labels(self):
        return {value: label for value, label in self.choices}

    def choice_label_from_api_data(self, data: Dict[str, Union[str, int]]) -> str:
        count = f"{data['doc_count']:,}"
        try:
            return f"{data['label']} ({count})"
        except KeyError:
            pass
        try:
            return f"{self.original_choice_labels[data['key']]} ({count})"
        except KeyError:
            pass
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
    levels = DynamicMultipleChoiceField(
        label="Level",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"},
        ),
        required=False,
    )
    topics = DynamicMultipleChoiceField(
        label="Topics",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    collections = DynamicMultipleChoiceField(
        label="Collections",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    closure_statuses = DynamicMultipleChoiceField(
        label="Closure Status",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    catalogue_sources = DynamicMultipleChoiceField(
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

        cleaned_data["filter_aggregations"] = (
            [cleaned_data.get("group")]
            + cleaned_data.get("levels")
            + cleaned_data.get("topics")
            + cleaned_data.get("collections")
            + cleaned_data.get("closure_statuses")
            + cleaned_data.get("catalogue_sources")
        )

        return cleaned_data

    def update_from_response(self, *, response):
        """Populate dynamic fields choices using aggregation data from API."""
        aggregations = response["aggregations"]

        self.fields["levels"].update_from_aggregations(
            aggregations.get("level", {}).get("buckets")
        )
        self.fields["topics"].update_from_aggregations(
            aggregations.get("topic", {}).get("buckets")
        )
        self.fields["collections"].update_from_aggregations(
            aggregations.get("collection", {}).get("buckets")
        )
        self.fields["closure_statuses"].update_from_aggregations(
            aggregations.get("closure", {}).get("buckets")
        )
        self.fields["catalogue_sources"].update_from_aggregations(
            aggregations.get("catalogueSource", {}).get("buckets")
        )

    def selected_filters(self):
        """List of selected filters, keyed by the corresponding field name.

        Used by template to output a list of selected filters.

        Method must be called on a bound form (post validation)

        Note: selected filters differ from the filter_aggregations passed to
        the client as 'group' isn't considered to be a filter.

        """
        return {
            "levels": self.cleaned_data.get("levels"),
            "topics": self.cleaned_data.get("topics"),
            "collections": self.cleaned_data.get("collections"),
            "closure_statuses": self.cleaned_data.get("closure_statuses"),
            "catalogue_sources": self.cleaned_data.get("catalogue_sources"),
        }


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
