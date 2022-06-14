import logging

from datetime import datetime
from typing import Dict, List, Union

from django import forms
from django.core.validators import MinLengthValidator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..ciim.client import SortBy, SortOrder
from ..ciim.constants import (
    CATALOGUE_BUCKETS,
    COLLECTION_CHOICES,
    LEVEL_CHOICES,
    WEBSITE_BUCKETS,
)

logger = logging.getLogger(__name__)


class DynamicMultipleChoiceField(forms.MultipleChoiceField):
    """MultipleChoiceField whose choices can be updated to reflect API response data."""

    def __init__(self, *args, **kwargs):
        self.validate_input = bool(kwargs.get("choices")) and kwargs.pop(
            "validate_input", True
        )
        super().__init__(*args, **kwargs)
        # The following attribue is used in templates to prevent rendering
        # unless choices have been updated to reflect options from the API
        self.choices_updated = False
        self.configured_choices = self.choices

    def valid_value(self, value):
        """Disable validation if the field choices are not yet set."""
        if not self.validate_input:
            return True
        return super().valid_value(value)

    @cached_property
    def configured_choice_labels(self):
        return {value: label for value, label in self.configured_choices}

    def choice_label_from_api_data(self, data: Dict[str, Union[str, int]]) -> str:
        count = f"{data['doc_count']:,}"
        try:
            # Use a label from the configured choice values, if available
            return f"{self.configured_choice_labels[data['key']]} ({count})"
        except KeyError:
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
        # Indicate that this field is okay to be rendered
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

    Seperated date fields naming convention ->
    <prefix>_start_day, <prefix>_start_month, <prefix>_start_year
    example "opening_start_day", "opening_start_year", "opening_start_year" in form
    corresponds to "openingStartDate" in API param
    """

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
    # Choices are supplied to this field to benefit validation. The labels
    # are the same as the API supplied values, so aren't of much benefit
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
    # Choices are supplied to this field to influence labels only. The options
    # are not complete enough to be used for validation
    collection = DynamicMultipleChoiceField(
        label="Collection",
        choices=COLLECTION_CHOICES,
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
        validate_input=False,
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
    held_by = DynamicMultipleChoiceField(
        label="Held By",
        widget=forms.widgets.CheckboxSelectMultiple(
            attrs={"class": "search-filters__list"}
        ),
        required=False,
    )
    opening_start_day = forms.CharField(
        max_length=2,
        label=_("Day"),
        required=False,
        widget=forms.TextInput(
            attrs={"size": 2, "placeholder": "DD", "inputmode": "numeric"}
        ),
    )
    opening_start_month = forms.CharField(
        max_length=2,
        label=_("Month"),
        required=False,
        widget=forms.TextInput(
            attrs={"size": 2, "placeholder": "MM", "inputmode": "numeric"}
        ),
    )
    opening_start_year = forms.CharField(
        max_length=4,
        label=_("Year"),
        required=False,
        widget=forms.TextInput(
            attrs={"size": 4, "placeholder": "YYYY", "inputmode": "numeric"}
        ),
    )
    opening_end_day = forms.CharField(
        max_length=2,
        label=_("Day"),
        required=False,
        widget=forms.TextInput(attrs={"size": 2, "placeholder": "DD"}),
    )
    opening_end_month = forms.CharField(
        max_length=2,
        label=_("Month"),
        required=False,
        widget=forms.TextInput(attrs={"size": 2, "placeholder": "MM"}),
    )
    opening_end_year = forms.CharField(
        max_length=4,
        label=_("Year"),
        required=False,
        widget=forms.TextInput(attrs={"size": 4, "placeholder": "YYYY"}),
    )
    per_page = forms.IntegerField(
        min_value=20,
        max_value=50,
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

    def _get_compressed_date_or_none_on_error(self, start_day: str, start_month: str, start_year: str) -> Union[None, datetime]:
        """
        Assumption: all params not required to belong to a real date. The Exception is bypassed to return None
        as error messages are customised for date and handled outside this method.
        Returns: valid date if all fields belong to a real date, otherwise None if invalid date.
        """
        try:
            return datetime(
                day=int(start_day), month=int(start_month), year=int(start_year)
            )
        except Exception as e:
            logger.debug(
                f"Error bypassed in _get_compressed_date_or_none_on_error: start_day={start_day}, start_month={start_month}, start_year={start_year} exception={e}"
            )
            return None

    def get_cleaned_date_parts(self, prefix_field_with_type: str) -> tuple[str, str, str]:
        """
        Returns tuple of cleaned seperated date fields

        Args:

        prefix_field_with_type:
        example when field is 'opening_start_day', prefix_field is 'opening', prefix_field_with_type is 'opening_start'
        """
        return (
            self.cleaned_data.get(prefix_field_with_type + "_day"),
            self.cleaned_data.get(prefix_field_with_type + "_month"),
            self.cleaned_data.get(prefix_field_with_type + "_year"),
        )

    def validate_dates(self, prefix_field: str) -> None:
        """
        Validates the date containing the prefix_field name and adds field error messages accordingly.
        As with individual fields, the <prefix>_start_year and <prefix>_end_year fields for populated for
        consolidated error messages.

        Args:

        prefix_field:
            Example when form field is 'opening_start_day', then prefix_field is 'opening'
        """
        start_date = None
        end_date = None

        start_day, start_month, start_year = self.get_cleaned_date_parts(
            prefix_field_with_type=prefix_field + "_start"
        )
        end_day, end_month, end_year = self.get_cleaned_date_parts(
            prefix_field_with_type=prefix_field + "_end"
        )

        # validate and make compressed start_date when all seperated fields are entered
        if start_day and start_month and start_year:
            start_date = self._get_compressed_date_or_none_on_error(
                start_day, start_month, start_year
            )
            if not start_date:
                # generic error for invalid date when all fields are provided
                self.add_error(
                    prefix_field + "_start_year", "Entered date must be a real date."
                )

        # validate and make compressed end_date when all seperated fields are entered
        if end_day and end_month and end_year:
            end_date = self._get_compressed_date_or_none_on_error(
                end_day, end_month, end_year
            )
            if not end_date:
                # generic error for invalid date when all fields are provided
                self.add_error(
                    prefix_field + "_end_year", "Entered date must be a real date."
                )

        # start date is empty or partial at this point
        if not start_date:
            # start date empty and not partial, when end date is empty or partial
            if not (start_day or start_month or start_year) and (
                end_day or end_month or end_year
            ):
                self.add_error(prefix_field + "_start_year", "Enter date")
            # start date is partial
            if start_day or start_month or start_year:
                if not start_day:
                    self.add_error(
                        prefix_field + "_start_day", "Date must include a day."
                    )
                if not start_month:
                    self.add_error(
                        prefix_field + "_start_month", "Date must include a month."
                    )
                if not start_year:
                    self.add_error(
                        prefix_field + "_start_year", "Date must include a year."
                    )

        # end date is empty or partial at this point
        if not end_date:
            # end date empty and not partial, when start date is empty or partial
            if not (end_day or end_month or end_year) and (
                start_day or start_month or start_year
            ):
                self.add_error(prefix_field + "_end_year", "Enter date")

            # end date is partial
            if end_day or end_month or end_year:
                if not end_day:
                    self.add_error(
                        prefix_field + "_end_day", "Date must include a day."
                    )
                if not end_month:
                    self.add_error(
                        prefix_field + "_end_month", "Date must include a month."
                    )
                if not end_year:
                    self.add_error(
                        prefix_field + "_end_year", "Date must include a year."
                    )

        if start_date and end_date:
            # both dates are valid at this point
            if start_date > end_date:
                self.add_error(
                    prefix_field + "_start_year", "Start date cannot be after end date"
                )

    def clean(self):
        """Collect selected filters to pass to the client in view."""
        cleaned_data = super().clean()

        self.validate_dates(prefix_field="opening")

        return cleaned_data


class CatalogueSearchForm(BaseCollectionSearchForm):
    group = forms.ChoiceField(
        label="bucket",
        choices=CATALOGUE_BUCKETS.as_choices(),
        required=False,
    )


class WebsiteSearchForm(BaseCollectionSearchForm):
    group = forms.ChoiceField(
        label="bucket",
        choices=WEBSITE_BUCKETS.as_choices(),
        required=False,
    )
