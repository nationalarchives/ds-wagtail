from django.test import SimpleTestCase

from ..forms import CatalogueSearchForm


class CatalogueSearchFormTest(SimpleTestCase):
    def test_empty_opening_start_date_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_end_date_0": "01",
                "opening_end_date_1": "12",
                "opening_end_date_2": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    def test_empty_opening_end_date_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_0": "01",
                "opening_start_date_1": "01",
                "opening_start_date_2": "2001",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    def test_opening_start_date_before_opening_end_date_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_0": "31",
                "opening_start_date_1": "12",
                "opening_start_date_2": "1999",
                "opening_end_date_0": "01",
                "opening_end_date_1": "01",
                "opening_end_date_2": "2000",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    def test_opening_date_empty_day_input_month_input_year_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_1": "12",
                "opening_start_date_2": "1999",
                "opening_end_date_1": "01",
                "opening_end_date_2": "2000",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    def test_opening_date_with_empty_day_empty_month_input_year_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_2": "1999",
                "opening_end_date_2": "2000",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    def test_opening_start_date_after_opening_end_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_0": "01",
                "opening_start_date_1": "01",
                "opening_start_date_2": "2000",
                "opening_end_date_0": "31",
                "opening_end_date_1": "12",
                "opening_end_date_2": "1999",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_date"], ["Start date cannot be after end date"]
        )

    def test_non_numeric_value_in_opening_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_0": "aa",
                "opening_start_date_1": "bb",
                "opening_start_date_2": "cccc",
                "opening_end_date_0": "dd",
                "opening_end_date_1": "ee",
                "opening_end_date_2": "ffff",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_date"],
            ["Entered date must be a real date, for example 23 9 2017."],
        )
        self.assertEqual(
            form.errors["opening_end_date"],
            ["Entered date must be a real date, for example 23 9 2017."],
        )

    def test_incorrect_day_in_opening_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_0": "99",
                "opening_start_date_1": "01",
                "opening_start_date_2": "2001",
                "opening_end_date_0": "98",
                "opening_end_date_1": "02",
                "opening_end_date_2": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_date"],
            ["Entered date must be a real date, for example 23 9 2017."],
        )
        self.assertEqual(
            form.errors["opening_end_date"],
            ["Entered date must be a real date, for example 23 9 2017."],
        )

    def test_incorrect_month_in_opening_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_0": "01",
                "opening_start_date_1": "99",
                "opening_start_date_2": "2001",
                "opening_end_date_0": "01",
                "opening_end_date_1": "98",
                "opening_end_date_2": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_date"],
            ["Entered date must be a real date, for example 23 9 2017."],
        )
        self.assertEqual(
            form.errors["opening_end_date"],
            ["Entered date must be a real date, for example 23 9 2017."],
        )

    def test_incorrect_year_in_opening_date_is_invalid(self):
        # day, month belong to correct range
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_0": "01",
                "opening_start_date_1": "01",
                "opening_start_date_2": "0",
                "opening_end_date_0": "31",
                "opening_end_date_1": "01",
                "opening_end_date_2": "0",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_date"],
            ["Entered date must be a real date, for example 23 9 2017."],
        )
        self.assertEqual(
            form.errors["opening_end_date"],
            ["Entered date must be a real date, for example 23 9 2017."],
        )

    def test_opening_date_with_empty_month_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_0": "01",
                "opening_start_date_2": "2001",
                "opening_end_date_0": "01",
                "opening_end_date_2": "2002",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_date"], ["Entered date must include a Month."]
        )
        self.assertEqual(
            form.errors["opening_end_date"], ["Entered date must include a Month."]
        )

    def test_opening_date_empty_year_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date_0": "01",
                "opening_start_date_1": "01",
                "opening_end_date_0": "01",
                "opening_end_date_1": "12",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_date"], ["Entered date must include a Year."]
        )
        self.assertEqual(
            form.errors["opening_end_date"], ["Entered date must include a Year."]
        )
