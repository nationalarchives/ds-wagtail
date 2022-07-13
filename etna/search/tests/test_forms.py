from django.test import SimpleTestCase

from ..forms import CatalogueSearchForm


class CatalogueSearchFormTest(SimpleTestCase):
    def test_start_date_after_end_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "opening_start_date": "2000-01-01",
                "opening_end_date": "1900-01-01",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["opening_start_date"], ["Start date cannot be after end date"]
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
