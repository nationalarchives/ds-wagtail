from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from etna.core.fields import DateInputField


class DateFieldValidatorTest(SimpleTestCase):
    def test_date_input_field_validators(self):
        """validates the overriden default messages"""
        for label, value, expected in (
            (
                "incorrect input with non numeric values for all fields",
                {"input_day": "aa", "input_month": "bb", "input_year": "cccc"},
                "Entered date must be a real date, for example 23 9 2017.",
            ),
            (
                "incorrect input with non numeric value for day",
                {"input_day": "aa", "input_month": "12", "input_year": "2001"},
                "Entered date must be a real date, for example 23 9 2017.",
            ),
            (
                "incorrect input with non numeric value for month",
                {"input_day": "31", "input_month": "13", "input_year": "2001"},
                "Entered date must be a real date, for example 23 9 2017.",
            ),
            (
                "incorrect input with non numeric value for year",
                {"input_day": "31", "input_month": "12", "input_year": "cccc"},
                "Entered date must be a real date, for example 23 9 2017.",
            ),
            (
                "incorrect input day with non positive value",
                {"input_day": "-99", "input_month": "01", "input_year": "2001"},
                "Entered date must be a real date, for example 23 9 2017.",
            ),
            (
                "incorrect input day with positive value and not in valid range",
                {"input_day": "99", "input_month": "01", "input_year": "2001"},
                "Entered date must be a real date, for example 23 9 2017.",
            ),
            (
                "incorrect input month with non positive value",
                {"input_day": "31", "input_month": "-13", "input_year": "2001"},
                "Entered date must be a real date, for example 23 9 2017.",
            ),
            (
                "incorrect input month with positive value and not in valid range",
                {"input_day": "31", "input_month": "13", "input_year": "2001"},
                "Entered date must be a real date, for example 23 9 2017.",
            ),
            (
                "incorrect input year non positive value",
                {"input_day": "31", "input_month": "12", "input_year": "-1"},
                "Entered date must be a real date, for example 23 9 2017.",
            ),
        ):
            with self.subTest(label):
                field = DateInputField(required=False)
                with self.assertRaisesMessage(ValidationError, expected):
                    value = field.clean(
                        [value["input_day"], value["input_month"], value["input_year"]]
                    )
