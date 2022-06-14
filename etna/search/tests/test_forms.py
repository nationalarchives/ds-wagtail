from django.test import SimpleTestCase

from ..forms import CatalogueSearchForm


class CatalogueSearchFormTest(SimpleTestCase):
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
            form.errors["opening_start_year"], ["Start date cannot be after end date"]
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
            form.errors["opening_start_year"], ["Entered date must be a real date."]
        )
        self.assertEqual(
            form.errors["opening_end_year"], ["Entered date must be a real date."]
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
            form.errors["opening_start_year"], ["Entered date must be a real date."]
        )
        self.assertEqual(
            form.errors["opening_end_year"], ["Entered date must be a real date."]
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
            form.errors["opening_start_year"], ["Entered date must be a real date."]
        )
        self.assertEqual(
            form.errors["opening_end_year"], ["Entered date must be a real date."]
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
            form.errors["opening_start_year"], ["Entered date must be a real date."]
        )
        self.assertEqual(
            form.errors["opening_end_year"], ["Entered date must be a real date."]
        )

    def test_empty_start_year_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_end_day": "01",
                "opening_end_month": "12",
                "opening_end_year": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(form.errors["opening_start_year"], ["Enter date"])

    def test_empty_end_year_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_day": "01",
                "opening_start_month": "01",
                "opening_start_year": "2001",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(form.errors["opening_end_year"], ["Enter date"])

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
            form.errors["opening_start_month"], ["Date must include a month."]
        )
        self.assertEqual(
            form.errors["opening_end_month"], ["Date must include a month."]
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
            form.errors["opening_start_year"], ["Date must include a year."]
        )
        self.assertEqual(form.errors["opening_end_year"], ["Date must include a year."])

    def test_empty_day_is_invalid(self):
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

        self.assertFalse(is_valid)
        self.assertEqual(form.errors["opening_start_day"], ["Date must include a day."])
        self.assertEqual(form.errors["opening_end_day"], ["Date must include a day."])
