from django.test import SimpleTestCase

from ..forms import CatalogueSearchForm


class CatalogueSearchFormTest(SimpleTestCase):
    def test_start_date_after_end_date_is_invalid(self):
        form = CatalogueSearchForm(
            {
                "group": "group:tna",
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
                "group": "group:tna",
                "opening_start_date": "1900-01-01",
                "opening_end_date": "2000-01-01",
            }
        )

        is_valid = form.is_valid()

        self.assertTrue(is_valid)


class CataglogueSearchFormSelectedFiltersTest(SimpleTestCase):
    def test_empty_form(self):
        form = CatalogueSearchForm({})

        form.is_valid()

        self.assertEqual(
            form.selected_filters(),
            {
                "levels": [],
                "topics": [],
                "collections": [],
                "closure_statuses": [],
                "catalogue_sources": [],
            },
        )

    def test_selected_group_is_excluded(self):
        form = CatalogueSearchForm(
            {
                "group": "group:tna",
            }
        )

        form.is_valid()

        self.assertEqual(
            form.selected_filters(),
            {
                "levels": [],
                "topics": [],
                "collections": [],
                "closure_statuses": [],
                "catalogue_sources": [],
            },
        )

    def test_selected_level(self):
        form = CatalogueSearchForm(
            {
                "group": "group:tna",
                "levels": ["level:level-one"],
            }
        )

        form.is_valid()

        self.assertEqual(
            form.selected_filters(),
            {
                "levels": ["level:level-one"],
                "topics": [],
                "collections": [],
                "closure_statuses": [],
                "catalogue_sources": [],
            },
        )

    def test_selected_topic(self):
        form = CatalogueSearchForm(
            {
                "group": "group:tna",
                "topics": ["topic:topic-one"],
            }
        )

        form.is_valid()

        self.assertEqual(
            form.selected_filters(),
            {
                "levels": [],
                "topics": ["topic:topic-one"],
                "collections": [],
                "closure_statuses": [],
                "catalogue_sources": [],
            },
        )

    def test_selected_closure_status(self):
        form = CatalogueSearchForm(
            {
                "group": "group:tna",
                "closure_statuses": ["closure:closure-status-one"],
            }
        )

        form.is_valid()

        self.assertEqual(
            form.selected_filters(),
            {
                "levels": [],
                "topics": [],
                "collections": [],
                "closure_statuses": ["closure:closure-status-one"],
                "catalogue_sources": [],
            },
        )

    def test_selected_catalogue_sources(self):
        form = CatalogueSearchForm(
            {
                "group": "group:tna",
                "catalogue_sources": ["catalogueSources:catalogue-source-one"],
            }
        )

        form.is_valid()

        self.assertEqual(
            form.selected_filters(),
            {
                "levels": [],
                "topics": [],
                "collections": [],
                "closure_statuses": [],
                "catalogue_sources": ["catalogueSources:catalogue-source-one"],
            },
        )
