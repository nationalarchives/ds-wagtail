import datetime

from django.test import SimpleTestCase

from etna.core.fields import END_OF_MONTH, DateInputField


class DateFieldTest(SimpleTestCase):
    def test_date_cleaned_valid_value(self):
        date = datetime.date(year=2007, month=12, day=11)
        field = DateInputField()
        value = field.clean([date.day, date.month, date.year])
        self.assertEqual(value, date)

    def test_start_date_default_day1_month1_for_empty_day_empty_month(self):
        input_day = input_month = ""
        input_year = "2007"
        date = datetime.date(year=int(input_year), month=1, day=1)
        field = DateInputField(required=False, default_day=1, default_month=1)
        value = field.clean([input_day, input_month, input_year])
        self.assertEqual(value, date)

    def test_start_date_default_day1_for_empty_day(self):
        input_day = ""
        input_month = "01"
        input_year = "2007"
        date = datetime.date(year=int(input_year), month=1, day=1)
        field = DateInputField(required=False, default_day=1, default_month=1)
        value = field.clean([input_day, input_month, input_year])
        self.assertEqual(value, date)

    def test_end_date_default_day31_for_empty_day(self):
        input_day = ""
        input_month = "01"
        input_year = "2007"
        date = datetime.date(year=int(input_year), month=int(input_month), day=31)
        field = DateInputField(
            required=False, default_day=END_OF_MONTH, default_month=12
        )
        value = field.clean([input_day, input_month, input_year])
        self.assertEqual(value, date)

    def test_end_date_default_day30_for_empty_day(self):
        input_day = ""
        input_month = "04"
        input_year = "2000"
        date = datetime.date(year=int(input_year), month=int(input_month), day=30)
        field = DateInputField(
            required=False, default_day=END_OF_MONTH, default_month=12
        )
        value = field.clean([input_day, input_month, input_year])
        self.assertEqual(value, date)

    def test_end_date_default_day29_for_empty_day(self):
        input_day = ""
        input_month = "02"
        input_year = "2000"
        date = datetime.date(year=int(input_year), month=int(input_month), day=29)
        field = DateInputField(
            required=False, default_day=END_OF_MONTH, default_month=12
        )
        value = field.clean([input_day, input_month, input_year])
        self.assertEqual(value, date)

    def test_end_date_default_day28_for_empty_day(self):
        input_day = ""
        input_month = "02"
        input_year = "2001"
        date = datetime.date(year=int(input_year), month=int(input_month), day=28)
        field = DateInputField(
            required=False, default_day=END_OF_MONTH, default_month=12
        )
        value = field.clean([input_day, input_month, input_year])
        self.assertEqual(value, date)

    def test_end_date_default_day31_month12_for_empty_day_empty_month(self):
        input_day = ""
        input_month = ""
        input_year = "2001"
        date = datetime.date(year=int(input_year), month=12, day=31)
        field = DateInputField(
            required=False, default_day=END_OF_MONTH, default_month=12
        )
        value = field.clean([input_day, input_month, input_year])
        self.assertEqual(value, date)
