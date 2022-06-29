from django.test import SimpleTestCase

from ..forms import CatalogueSearchForm


class CatalogueSearchFormTest(SimpleTestCase):
    expected_date_format_msg = "Entered date must be a real date, for example 23 9 2017"

    def test_start_date_after_end_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_day": "01",
                "opening_start_month": "01",
                "opening_start_year": "2000",
                "opening_end_day": "01",
                "opening_end_month": "01",
                "opening_end_year": "1900",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_day"], ["From date must be earlier than To date"]
        )

    def test_opening_start_date_before_opening_end_date_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date": "1900-01-01",
                "opening_end_date": "2000-01-01",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    def test_non_numeric_value_in_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_day": "aa",
                "opening_start_month": "bb",
                "opening_start_year": "cccc",
                "opening_end_day": "dd",
                "opening_end_month": "ee",
                "opening_end_year": "ffff",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_day"], [self.expected_date_format_msg]
        )
        self.assertEqual(
            form.errors["opening_end_day"], [self.expected_date_format_msg]
        )

    def test_incorrect_day_in_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_day": "99",
                "opening_start_month": "01",
                "opening_start_year": "2001",
                "opening_end_day": "98",
                "opening_end_month": "02",
                "opening_end_year": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_day"], [self.expected_date_format_msg]
        )
        self.assertEqual(
            form.errors["opening_end_day"], [self.expected_date_format_msg]
        )

    def test_incorrect_month_in_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_day": "01",
                "opening_start_month": "99",
                "opening_start_year": "2001",
                "opening_end_day": "01",
                "opening_end_month": "98",
                "opening_end_year": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_day"], [self.expected_date_format_msg]
        )
        self.assertEqual(
            form.errors["opening_end_day"], [self.expected_date_format_msg]
        )

    def test_incorrect_year_in_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_day": "01",
                "opening_start_month": "01",
                "opening_start_year": "0",
                "opening_end_day": "01",
                "opening_end_month": "12",
                "opening_end_year": "0",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_day"], [self.expected_date_format_msg]
        )
        self.assertEqual(
            form.errors["opening_end_day"], [self.expected_date_format_msg]
        )

    def test_empty_start_date_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_end_day": "01",
                "opening_end_month": "12",
                "opening_end_year": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    def test_empty_end_date_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_day": "01",
                "opening_start_month": "01",
                "opening_start_year": "2001",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    def test_empty_month_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_day": "01",
                "opening_start_year": "2001",
                "opening_end_day": "01",
                "opening_end_year": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_day"], ["Entered date must include a Month"]
        )
        self.assertEqual(
            form.errors["opening_end_day"], ["Entered date must include a Month"]
        )

    def test_empty_year_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_day": "01",
                "opening_start_month": "01",
                "opening_end_day": "01",
                "opening_end_month": "12",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_day"], ["Entered date must include a Year"]
        )
        self.assertEqual(
            form.errors["opening_end_day"], ["Entered date must include a Year"]
        )

    def test_empty_day_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_month": "01",
                "opening_start_year": "2001",
                "opening_end_month": "12",
                "opening_end_year": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    def test_empty_day_month_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_year": "2001",
                "opening_end_year": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    def test_empty_day_year_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_month": "01",
                "opening_end_month": "02",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_day"],
            ["Entered date must include a Year"],
        )
        self.assertEqual(
            form.errors["opening_end_day"], ["Entered date must include a Year"]
        )

    def test_empty_month_year_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_day": "01",
                "opening_end_day": "02",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_day"],
            ["Entered date must include a Year"],
        )
        self.assertEqual(
            form.errors["opening_end_day"],
            ["Entered date must include a Year"],
        )
