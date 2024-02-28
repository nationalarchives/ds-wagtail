from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from etna.core.fields import DateInputField

from ..fields import ERR_MSG_REAL_DATE


class DateFieldValidatorTest(SimpleTestCase):
    def test_date_input_for_day_field_validator(self):
        """validates the overriden default message for day field"""
        field = DateInputField(required=False)
        for label, value, expected in (
            (
                "incorrect input with non numeric value for day",
                {"input_day": "aa", "input_month": "12", "input_year": "2001"},
                ERR_MSG_REAL_DATE,
            ),
            (
                "incorrect input day with non positive value",
                {"input_day": "-99", "input_month": "01", "input_year": "2001"},
                ERR_MSG_REAL_DATE,
            ),
            (
                "incorrect input day with positive value and not in valid range",
                {"input_day": "99", "input_month": "01", "input_year": "2001"},
                ERR_MSG_REAL_DATE,
            ),
        ):
            with self.subTest(label):
                with self.assertRaisesMessage(ValidationError, expected):
                    value = field.clean(
                        [value["input_day"], value["input_month"], value["input_year"]]
                    )

    def test_date_input_for_month_field_validator(self):
        """validates the overriden default message for month field"""
        field = DateInputField(required=False)
        for label, value, expected in (
            (
                "incorrect input with non numeric value for month",
                {"input_day": "31", "input_month": "bb", "input_year": "2001"},
                ERR_MSG_REAL_DATE,
            ),
            (
                "incorrect input month with non positive value",
                {"input_day": "31", "input_month": "-13", "input_year": "2001"},
                ERR_MSG_REAL_DATE,
            ),
            (
                "incorrect input month with positive value and not in valid range",
                {"input_day": "31", "input_month": "13", "input_year": "2001"},
                ERR_MSG_REAL_DATE,
            ),
        ):
            with self.subTest(label):
                with self.assertRaisesMessage(ValidationError, expected):
                    value = field.clean(
                        [value["input_day"], value["input_month"], value["input_year"]]
                    )

    def test_date_input_for_year_field_validator(self):
        """validates the overriden default message for year field"""
        field = DateInputField(required=False)
        for label, value, expected in (
            (
                "incorrect input with non numeric values for all fields",
                {"input_day": "aa", "input_month": "bb", "input_year": "cccc"},
                ERR_MSG_REAL_DATE,
            ),
            (
                "incorrect input with non numeric value for year",
                {"input_day": "31", "input_month": "12", "input_year": "cccc"},
                ERR_MSG_REAL_DATE,
            ),
            (
                "incorrect input year non positive value",
                {"input_day": "31", "input_month": "12", "input_year": "-1"},
                ERR_MSG_REAL_DATE,
            ),
        ):
            with self.subTest(label):
                with self.assertRaisesMessage(ValidationError, expected):
                    value = field.clean(
                        [value["input_day"], value["input_month"], value["input_year"]]
                    )
