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

    def _get_compressed_date_or_none_on_error(
        self, start_day: str, start_month: str, start_year: str
    ) -> Union[None, datetime]:
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

    def get_cleaned_date_parts(
        self, prefix_field_with_type: str
    ) -> tuple[str, str, str]:
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

    def get_blank_parts_for_start_date(
        self, start_day: str, start_month: str, start_year: str
    ) -> tuple[str, str, str]:
        """
        Assumption: day/month can be blank; year must be valid
        Returns date parts filled with valid date values if blank, otherwise same date parts
        """
        if start_year:
            if not start_day:
                start_day = "01"
            if not start_month:
                start_month = "01"
        return (start_day, start_month, start_year)

    def get_blank_parts_for_end_date(
        self, end_day: str, end_month: str, end_year: str
    ) -> tuple[str, str, str]:
        """
        Assumption: day/month can be blank; year must be valid
        Returns date parts filled with valid date values if blank, otherwise same date parts
        """
        import calendar

        if end_year:
            if not end_day:
                if not end_month:
                    end_month = "12"
                # covers date ending '28/29/30/31'
                end_day = str(calendar.monthrange(int(end_year), int(end_month))[1])
        return (end_day, end_month, end_year)

    def validate_dates(self, prefix_field: str) -> None:
        """
        Validates the date containing the prefix_field name and adds field error messages accordingly.
        The <prefix>_start_day and <prefix>_end_day fields for populated for error messages related
        to individual date fields.

        Date Inputs: DD-MM-YYYY, MM-YYYY, YYYY, Start Date, End Date, Both Start Date and End Date

        Args:

        prefix_field:
            Example when form field is 'opening_start_day', then prefix_field is 'opening'
        """
        start_date = None
        end_date = None
        input_error_start_date = False
        input_error_end_date = False
        date_format_msg = "Entered date must be a real date, for example 23 9 2017"

        start_day, start_month, start_year = self.get_cleaned_date_parts(
            prefix_field_with_type=prefix_field + "_start"
        )
        end_day, end_month, end_year = self.get_cleaned_date_parts(
            prefix_field_with_type=prefix_field + "_end"
        )

        if start_day or start_month or start_year:
            try:
                if start_day and not (1 <= int(start_day) <= 31):
                    raise ValueError(f"Value '{start_day}' not between 1 and 31")
                if start_month and not (1 <= int(start_month) <= 12):
                    raise ValueError(f"Value '{start_month}' not between 1 and 12")
                if start_year and not (1 <= int(start_year) <= 9999):
                    raise ValueError(f"Value '{start_year}' not between 1 and 9999")
                # DD/MM, DD-MM
                if (start_day or start_month) and not start_year:
                    # DD-MM
                    if start_day and start_month:
                        max_days_in_month = {
                            1: 31,
                            2: 29,
                            3: 31,
                            4: 30,
                            5: 31,
                            6: 30,
                            7: 31,
                            8: 31,
                            9: 30,
                            10: 31,
                            11: 30,
                            12: 31,
                        }
                        if not (
                            1 <= int(start_day) <= max_days_in_month[int(start_month)]
                        ):
                            raise ValueError(
                                f"Value '{start_day}' not between 1 and {max_days_in_month[int(start_month)]}"
                            )
                    # DD/MM
                    self.add_error(
                        prefix_field + "_start_day", "Entered date must include a Year"
                    )
                # DD-YYYY
                elif (start_day and start_year) and not start_month:
                    self.add_error(
                        prefix_field + "_start_day", "Entered date must include a Month"
                    )
                else:
                    # YYYY, MM-YYYY
                    (
                        start_day,
                        start_month,
                        start_year,
                    ) = self.get_blank_parts_for_start_date(
                        start_day, start_month, start_year
                    )
            except ValueError:
                input_error_start_date = True
                self.add_error(prefix_field + "_start_day", date_format_msg)

        if end_day or end_month or end_year:
            try:
                if end_day and not (1 <= int(end_day) <= 31):
                    raise ValueError(f"Value '{end_day}' not between 1 and 31")
                if end_month and not (1 <= int(end_month) <= 12):
                    raise ValueError(f"Value '{end_month}' not between 1 and 12")
                if end_year and not (1 <= int(end_year) <= 9999):
                    raise ValueError(f"Value '{end_year}' not between 1 and 9999")
                # DD/MM, DD-MM
                if (end_day or end_month) and not end_year:
                    # DD-MM
                    if end_day and end_month:
                        max_days_in_month = {
                            1: 31,
                            2: 29,
                            3: 31,
                            4: 30,
                            5: 31,
                            6: 30,
                            7: 31,
                            8: 31,
                            9: 30,
                            10: 31,
                            11: 30,
                            12: 31,
                        }
                        if not (1 <= int(end_day) <= max_days_in_month[int(end_month)]):
                            raise ValueError(
                                f"Value '{end_day}' not between 1 and {max_days_in_month[int(end_month)]}"
                            )
                    # DD/MM
                    self.add_error(
                        prefix_field + "_end_day", "Entered date must include a Year"
                    )
                # DD-YYYY
                elif (end_day and end_year) and not end_month:
                    self.add_error(
                        prefix_field + "_end_day", "Entered date must include a Month"
                    )
                else:
                    # YYYY, MM-YYYY
                    end_day, end_month, end_year = self.get_blank_parts_for_end_date(
                        end_day, end_month, end_year
                    )

            except ValueError:
                input_error_end_date = True
                self.add_error(prefix_field + "_end_day", date_format_msg)

        # DD-MM-YYYY
        # validate and make compressed start_date when all seperated fields are entered
        if not input_error_start_date and start_day and start_month and start_year:
            start_date = self._get_compressed_date_or_none_on_error(
                start_day, start_month, start_year
            )
            if not start_date:
                # generic error for invalid date when all fields are provided
                self.add_error(prefix_field + "_start_day", date_format_msg)

        # validate and make compressed end_date when all seperated fields are entered
        if not input_error_end_date and end_day and end_month and end_year:
            end_date = self._get_compressed_date_or_none_on_error(
                end_day, end_month, end_year
            )
            if not end_date:
                # generic error for invalid date when all fields are provided
                self.add_error(prefix_field + "_end_day", date_format_msg)

        if start_date and end_date:
            # both dates are valid at this point
            if start_date > end_date:
                self.add_error(
                    prefix_field + "_start_day",
                    "From date must be earlier than To date",
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
