from django.test import SimpleTestCase

from ..forms import CatalogueSearchForm


class SearchFormTest(SimpleTestCase):
    def test_start_date_after_end_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "group:tna",
                "start_date": "2000-01-01",
                "end_date": "1900-01-01",
            }
        )

        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["start_date"], ["Start date cannot be after end date"]
        )

    def test_start_date_before_end_date_is_valid(self):
        form = CatalogueSearchForm(
            {
                "group": "group:tna",
                "start_date": "1900-01-01",
                "end_date": "2000-01-01",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)
