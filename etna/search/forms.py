from django import forms
from django.core.validators import MinLengthValidator

from ..ciim.client import SortBy, SortOrder


class DynamicMultipleChoiceField(forms.MultipleChoiceField):
    """MultipleChoiceField whose choices are populated by API response data.

    Valid filter options are returned by the API as aggregation data belong to
    a result set.

    This field populates its choice list from aggregation data. This means that
    at the point of form validation, this field's choices are empty.
    """

    def __init__(self, filter_key, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # prefix when passing to filter_aggregations. Format <prefix>:<key>
        self.filter_key = filter_key

    def valid_value(self, value):
        """Disable validation, field doesn't have choices until the API is called."""
        return True

    def update_from_aggregations(self, aggregations):
        """Populate choice list with aggregation data."""
        self.choices = [
            (f"{self.filter_key}:{i['key']}", f"{i['key']} ({i['doc_count']:,})")
            for i in aggregations
        ]


class FeaturedSearchForm(forms.Form):
    q = forms.CharField(
        label="Search here",
        # If no query is provided, pass None to client to fetch all results.
        empty_value=None,
        required=False,
        validators=[MinLengthValidator(2)],
    )


class SearchForm(forms.Form):
    q = forms.CharField(
        label="Search term",
        # If no query is provided, pass None to client to fetch all results.
        empty_value=None,
        required=False,
        widget=forms.TextInput(attrs={"class": "search-results-hero__form-search-box"}),
    )
    filter_keyword = forms.CharField(
        label="Search within",
        # If no filter_keyword is provided, pass None to client bypass search within
        empty_value=None,
        required=False,
        widget=forms.TextInput(attrs={"class": "search-filters__search"}),
    )
    group = forms.ChoiceField(
        label="bucket",
        choices=[
            ("group:tna", "TNA"),
            ("group:nonTna", "NonTNA"),
            ("group:creator", "Creator"),
            ("group:archive", "Archive"),
        ],
    )
    levels = DynamicMultipleChoiceField(
        label="Level",
        filter_key="level",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    topics = DynamicMultipleChoiceField(
        label="Topics",
        filter_key="topic",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    collections = DynamicMultipleChoiceField(
        label="Collections",
        filter_key="collection",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    closure_statuses = DynamicMultipleChoiceField(
        label="Closure Status",
        filter_key="closure",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    catalogue_sources = DynamicMultipleChoiceField(
        label="Catalogue Sources",
        filter_key="catalogueSource",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "input", "placeholder": "YYYY-MM-DD"}
        ),
        required=False,
    )
    end_date = forms.DateTimeField(
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

    def clean(self):
        """Collect selected filters to pass to the client in view."""
        cleaned_data = super().clean()

        try:
            if cleaned_data.get("start_date") > cleaned_data.get("end_date"):
                self.add_error("start_date", "Start date cannot be after end date")
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

        self.fields["levels"].update_from_aggregations(aggregations["level"]["buckets"])
        self.fields["topics"].update_from_aggregations(aggregations["topic"]["buckets"])
        self.fields["collections"].update_from_aggregations(
            aggregations["collection"]["buckets"]
        )
        self.fields["closure_statuses"].update_from_aggregations(
            aggregations["closure"]["buckets"]
        )
        self.fields["catalogue_sources"].update_from_aggregations(
            aggregations["catalogueSource"]["buckets"]
        )
