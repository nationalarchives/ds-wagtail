import datetime

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from etna.core.fields import END_OF_MONTH, DateInputField

from ..fields import ERR_MSG_REAL_DATE


class DateFieldTest(SimpleTestCase):
    def test_date_cleaned_valid_date(self):
        date = datetime.date(year=2007, month=12, day=11)
        field = DateInputField()
        value = field.clean([date.day, date.month, date.year])
        self.assertEqual(value, date)

    def test_various_inputs_with_dtf_default_for_start_date(self):
        """date field with defaults for start date"""
        field = DateInputField(required=False, default_day=1, default_month=1)
        for label, value, expected in (
            (
                "input yyyy with ddmm empty",
                {"input_day": "", "input_month": "", "input_year": "2007"},
                datetime.date(year=2007, month=1, day=1),
            ),
            (
                "input mmyyyy with dd empty",
                {"input_day": "", "input_month": "01", "input_year": "2007"},
                datetime.date(year=2007, month=1, day=1),
            ),
        ):
            with self.subTest(label):
                value = field.clean(
                    [value["input_day"], value["input_month"], value["input_year"]]
                )
                self.assertEqual(value, expected, label)

    def test_various_inputs_with_dtf_default_for_end_date(self):
        """date field with defaults for end date"""
        field = DateInputField(
            required=False, default_day=END_OF_MONTH, default_month=12
        )
        for label, value, expected in (
            (
                "with empty day input 31-days-in-month",
                {"input_day": "", "input_month": "01", "input_year": "2007"},
                datetime.date(year=2007, month=1, day=31),
            ),
            (
                "with empty day input 30-days-in-month",
                {"input_day": "", "input_month": "04", "input_year": "2000"},
                datetime.date(year=2000, month=4, day=30),
            ),
            (
                "with empty day input 29-days-in-month",
                {"input_day": "", "input_month": "02", "input_year": "2000"},
                datetime.date(year=2000, month=2, day=29),
            ),
            (
                "with empty day input 28-days-in-month",
                {"input_day": "", "input_month": "02", "input_year": "2001"},
                datetime.date(year=2001, month=2, day=28),
            ),
            (
                "with empty day, month input ddmm becomes end-of-year",
                {"input_day": "", "input_month": "", "input_year": "2007"},
                datetime.date(year=2007, month=12, day=31),
            ),
        ):
            with self.subTest(label):
                value = field.clean(
                    [value["input_day"], value["input_month"], value["input_year"]]
                )
                self.assertEqual(value, expected, label)

    def test_date_cleaned_without_validators(self):
        """validates exception raised in clean method when using dateinputfield defaults"""
        field = DateInputField(
            required=False, default_day=END_OF_MONTH, default_month=12
        )
        for label, value, expected in (
            (
                "incorrect day range for month",
                {"input_day": "31", "input_month": "02", "input_year": "2001"},
                ERR_MSG_REAL_DATE,
            ),
            (
                "incorrect year but position year",
                {"input_day": "31", "input_month": "02", "input_year": "0"},
                ERR_MSG_REAL_DATE,
            ),
            (
                "input month is empty dd<empty>yyyy",
                {"input_day": "01", "input_month": "", "input_year": "2007"},
                "Entered date must include a month.",
            ),
            (
                "input year is empty ddmm<empty>",
                {"input_day": "01", "input_month": "01", "input_year": ""},
                "Entered date must include a year.",
            ),
        ):
            with self.subTest(label):
                with self.assertRaisesMessage(ValidationError, expected):
                    value = field.clean(
                        [value["input_day"], value["input_month"], value["input_year"]]
                    )

    def test_date_cleaned_without_defaults_without_validators(self):
        """validates exception raised in clean method when without dateinputfield defaults"""
        field = DateInputField(required=False)
        for label, value, expected in (
            (
                "input month is empty dd<empty>yyyy",
                {"input_day": "01", "input_month": "", "input_year": "2007"},
                ERR_MSG_REAL_DATE,
            ),
            (
                "input year is empty ddmm<empty>",
                {"input_day": "01", "input_month": "01", "input_year": ""},
                ERR_MSG_REAL_DATE,
            ),
            (
                "input day is empty <empty>mmyyyy",
                {"input_day": "", "input_month": "01", "input_year": "2007"},
                ERR_MSG_REAL_DATE,
            ),
        ):
            with self.subTest(label):
                with self.assertRaisesMessage(ValidationError, expected):
                    value = field.clean(
                        [value["input_day"], value["input_month"], value["input_year"]]
                    )
