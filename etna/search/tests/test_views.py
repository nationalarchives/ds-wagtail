import json as json_module
import unittest

from typing import Any, Dict

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse, reverse_lazy

from wagtail.test.utils import WagtailTestUtils

import responses

from etna.core.test_utils import prevent_request_warnings

from ..forms import CatalogueSearchForm
from ..views import CatalogueSearchView


@override_settings(
    CLIENT_BASE_URL=f"{settings.CLIENT_BASE_URL}",
)
class SearchViewTestCase(WagtailTestUtils, TestCase):
    maxDiff = None

    def setUp(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json={
                "data": [],
                "aggregations": [],
            },
        )


class BadRequestHandlingTest(SearchViewTestCase):
    test_url = reverse_lazy("search-catalogue")

    @prevent_request_warnings
    def test_httpresponsebadrequest_recieved_when_bad_values_provided(self):
        for field_name, value in [
            ("group", "foo"),
            ("per_page", "bar"),
            ("per_page", 10000),
            ("sort", "baz"),
            ("display", "foo"),
        ]:
            with self.subTest(f"{field_name} = {value}"):
                response = self.client.get(self.test_url, data={field_name: value})
                self.assertEqual(response.status_code, 400)


@unittest.skip("TODO:Rosetta")
class SelectedFiltersTest(SimpleTestCase):
    def get_result(self, form):
        return CatalogueSearchView().get_selected_filters(form)

    def test_with_valid_filter_values(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "topic": ["topic-one"],
                "level": ["Division"],
                "collection": ["WO", "AK"],
                "country": ["England", "Yorkshire, North Riding"],
                "location": ["Australia", "United States of America"],
            }
        )

        self.assertTrue(form.is_valid())

        self.assertEqual(
            self.get_result(form),
            {
                "collection": [
                    (
                        "WO",
                        "WO - War Office, Armed Forces, Judge Advocate General, and related bodies",
                    ),
                    ("AK", "AK - County Courts"),
                ],
                "level": [("Division", "Division")],
                "topic": [("topic-one", "topic-one")],
                "country": [
                    ("England", "England"),
                    ("Yorkshire, North Riding", "Yorkshire, North Riding"),
                ],
                "location": [
                    ("Australia", "Australia"),
                    ("United States of America", "United States of America"),
                ],
            },
        )

    def test_counts_are_removed_from_updated_choice_labels(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "topic": ["topic-one"],
                "level": ["Division"],
            }
        )
        self.assertTrue(form.is_valid())

        topic_field = form.fields["topic"]
        level_field = form.fields["level"]

        # Update topic field choices to include counts on labels
        topic_field.update_choices(
            [
                {"key": "topic-one", "doc_count": 10},
            ]
        )
        self.assertEqual(topic_field.choices, [("topic-one", "topic-one (10)")])

        # Update level field choices to include counts on labels
        level_field.update_choices(
            [
                {
                    "key": "Division",
                    "doc_count": 10,
                },
            ]
        )
        self.assertEqual(level_field.choices, [("Division", "Division (10)")])

        self.assertEqual(
            self.get_result(form),
            {
                "topic": [("topic-one", "topic-one")],
                "level": [("Division", "Division")],
            },
        )

    def test_with_invalid_filter_values(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                # only the 'level' field validates values against the choices
                "level": ["foo"],
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(self.get_result(form), {})

    def test_with_partially_invalid_filter_values(self):
        form = CatalogueSearchForm(
            {
                "group": "tna",
                "topic": ["topic-one", "topic-two"],  # valid
                "catalogue_source": ["catalogue-source-one"],  # valid
                "collection": ["bar"],
                "country": ["England", "Yorkshire, North Riding"],  # valid
                "location": ["Australia", "United States of America"],  # valid
                "level": ["foo"],  # invalid
            }
        )

        self.assertFalse(form.is_valid())

        self.assertEqual(
            self.get_result(form),
            {
                "collection": [
                    ("bar", "bar"),
                ],
                "topic": [
                    ("topic-one", "topic-one"),
                    ("topic-two", "topic-two"),
                ],
                "catalogue_source": [
                    ("catalogue-source-one", "catalogue-source-one"),
                ],
                "country": [
                    ("England", "England"),
                    ("Yorkshire, North Riding", "Yorkshire, North Riding"),
                ],
                "location": [
                    ("Australia", "Australia"),
                    ("United States of America", "United States of America"),
                ],
            },
        )


@unittest.skip("TODO:Rosetta")
class CatalogueSearchAPIIntegrationTest(SearchViewTestCase):
    test_url = reverse_lazy("search-catalogue")

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get(self.test_url)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                f"{settings.CLIENT_BASE_URL}/search"
                "?stream=evidential"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=group%3A30"
                "&aggregations=collection%3A10"
                "&aggregations=level%3A10"
                "&aggregations=closure%3A10"
                "&filterAggregations=group%3Atna"
                "&from=0"
                "&size=20"
            ),
        )


@override_settings(CLIENT_BASE_URL=f"{settings.CLIENT_BASE_URL}")
class EndToEndSearchTestCase(TestCase):
    # The following HTML snippets must be updated to reflect any future HTML changes
    results_html = '<ul class="search-results__list" id="analytics-results-list">'
    no_results_messaging_html = '<div class="no-results">'
    bucket_links_html = (
        '<ul class="search-buckets__list" data-id="search-buckets-list">'
    )
    search_within_option_html = '<label for="id_filter_keyword" class="tna-heading-s search-filters__label--block">Search within results</label>'
    sort_desktop_options_html = '<label for="id_sort_desktop">Sort by</label>'
    sort_mobile_options_html = '<label for="id_sort_mobile">Sort by</label>'
    filter_options_html = '<form method="GET" data-id="filters-form"'

    def patch_api_endpoint(self, url: str, fixture_path: str):
        full_fixture_path = (
            settings.BASE_DIR + "/etna/search/tests/fixtures/" + fixture_path
        )
        fixture_content = ""
        with open(full_fixture_path) as f:
            fixture_content = json_module.loads(f.read())
        responses.add(responses.GET, url, json=fixture_content, status=200)

    def patch_search_endpoint(self, fixture_path: str):
        self.patch_api_endpoint(f"{settings.CLIENT_BASE_URL}/search", fixture_path)

    def assertNoResultsMessagingRendered(self, response):
        self.assertIn(self.no_results_messaging_html, response)

    def assertNoResultsMessagingNotRendered(self, response):
        self.assertNotIn(self.no_results_messaging_html, response)

    def assertBucketLinksRendered(self, response):
        self.assertIn(self.bucket_links_html, response)

    def assertBucketLinksNotRendered(self, response):
        self.assertNotIn(self.bucket_links_html, response)

    def assertSearchWithinOptionRendered(self, response):
        self.assertIn(self.search_within_option_html, response)

    def assertSearchWithinOptionNotRendered(self, response):
        self.assertNotIn(self.search_within_option_html, response)

    def assertSortOptionsRendered(self, response):
        self.assertIn(self.sort_desktop_options_html, response)
        self.assertIn(self.sort_mobile_options_html, response)

    def assertSortOptionsNotRendered(self, response):
        self.assertNotIn(self.sort_desktop_options_html, response)
        self.assertNotIn(self.sort_mobile_options_html, response)

    def assertFilterOptionsRendered(self, response):
        self.assertIn(self.filter_options_html, response)

    def assertFilterOptionsNotRendered(self, response):
        self.assertNotIn(self.filter_options_html, response)

    def assertResultsRendered(self, response):
        self.assertIn(self.results_html, response)

    def assertResultsNotRendered(self, response):
        self.assertNotIn(self.results_html, response)


@unittest.skip("TODO:Rosetta")
class CatalogueSearchEndToEndTest(EndToEndSearchTestCase):
    test_url = reverse_lazy("search-catalogue")

    @responses.activate
    def test_no_matches_for_q_param_only_search(self):
        """
        When a user does an initial search for something with no matches:

        They SHOULD see:
        - A "No results" message

        They SHOULD NOT see:
        - Names, result counts and links for all buckets
        - A "Search within these results" option
        - Options to change sort order and display style of results
        - Filter options to refine the search
        - Search results
        """

        self.patch_search_endpoint("catalogue_search_no_results.json")
        response = self.client.get(self.test_url, data={"q": "foobar"})
        content = str(response.content)

        # SHOULD see
        self.assertNoResultsMessagingRendered(content)

        # SHOULD NOT see
        self.assertBucketLinksNotRendered(content)
        self.assertSearchWithinOptionNotRendered(content)
        self.assertSortOptionsNotRendered(content)
        self.assertFilterOptionsNotRendered(content)
        self.assertResultsNotRendered(content)

    @responses.activate
    def test_no_matches_for_the_refined_search(self):
        """
        When a user is viewing a bucket with results for the original search,
        then uses the "Search within these results" option to refine it, and
        that 'refined' search has no results:

        They SHOULD see:
        - Names, result counts and links for all buckets
        - A "Search within these results" option
        - Options to change sort order and display style of results
        - Filter options to refine the search
        - A "No results" message.

        They SHOULD NOT see:
        - Search results
        """

        self.patch_search_endpoint("catalogue_search_empty_when_refined.json")
        response = self.client.get(
            self.test_url,
            data={"q": "japan", "filter_keyword": "qwerty"},
        )
        content = str(response.content)

        # SHOULD see
        self.assertBucketLinksRendered(content)
        self.assertSearchWithinOptionRendered(content)
        self.assertSortOptionsRendered(content)
        self.assertNoResultsMessagingRendered(content)
        self.assertFilterOptionsRendered(content)

        # SHOULD NOT see
        self.assertResultsNotRendered(content)

    @responses.activate
    def test_refined_search_with_matches(self):
        """
        When a user is viewing a bucket with results for the original search,
        then uses the "Search within these results" option to refine it, and
        that 'refined' search has results:

        They SHOULD see:
        - Names, result counts and links for all buckets
        - A "Search within these results" option
        - Options to change sort order and display style of results
        - Filter options to refine the search
        - Search results

        They SHOULD NOT see:
        -  A "No results" message.
        """

        self.patch_search_endpoint("catalogue_search_refined_with_matches.json")
        response = self.client.get(
            self.test_url,
            data={
                "q": "japan",
                "group": "nonTna",
                "held_by": "London Metropolitan Archives: City of London",
            },
        )
        content = str(response.content)

        # SHOULD see
        self.assertBucketLinksRendered(content)
        self.assertSearchWithinOptionRendered(content)
        self.assertSortOptionsRendered(content)
        self.assertFilterOptionsRendered(content)
        self.assertResultsRendered(content)

        # SHOULD NOT see
        self.assertNoResultsMessagingNotRendered(content)

    @responses.activate
    def test_selected_filter_options_remain_visible(self):
        """
        When a user is viewing search results for a particular bucket,
        then uses filter options to further refine that search,
        all selected filters should remain available as filter options,
        even if they were excluded from the API results 'aggregations'
        list due to not having any matches.

        Test covers create session info for Catalogue search with query.
        """
        self.patch_search_endpoint("catalogue_search_with_multiple_filters.json")

        expected_url = "/search/catalogue/?q=test%2Bsearch%2Bterm&group=tna&collection=DEFE&collection=HW&collection=RGO&level=Piece&closure=Open%2BDocument%252C%2BOpen%2BDescription"

        response = self.client.get(
            self.test_url,
            data={
                "q": "test+search+term",
                "group": "tna",
                "collection": ["DEFE", "HW", "RGO"],
                "level": "Piece",
                "closure": "Open+Document%2C+Open+Description",
            },
        )
        session = self.client.session
        content = str(response.content)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(session.get("back_to_search_url"), expected_url)

        self.assertIn('<input type="checkbox" name="collection" value="DEFE"', content)
        self.assertIn('<input type="checkbox" name="collection" value="HW"', content)
        self.assertIn('<input type="checkbox" name="collection" value="RGO"', content)

    @responses.activate
    def test_render_invalid_date_range_message(self):
        """
        When a user does search with an invalid date range:

        They SHOULD see:
        - A "No results" message in search results
        - Particular message from "No results"
        - A "Search within these results" option
        - Error message next to the 'to' date field
        """
        for from_date_field, to_date_field in (
            ("opening_start_date", "opening_end_date"),
            ("covering_date_from", "covering_date_to"),
        ):
            response = self.client.get(
                self.test_url,
                data={
                    "group": "tna",
                    f"{from_date_field}_0": "01",
                    f"{from_date_field}_1": "01",
                    f"{from_date_field}_2": "2000",
                    f"{to_date_field}_0": "01",
                    f"{to_date_field}_1": "01",
                    f"{to_date_field}_2": "1999",
                    "q": "london",
                    "filter_keyword": "kew",
                },
            )
            content = str(response.content)

            # SHOULD see
            self.assertNoResultsMessagingRendered(content)
            self.assertIn("<li>Try different spellings or search terms</li>", content)
            self.assertSearchWithinOptionRendered(content)
            self.assertIn(from_date_field, response.context["form"].errors)
            self.assertIn(
                "<li>This date must be earlier than or equal to the &#x27;to&#x27; date.</li>",
                content,
            )


@unittest.skip("TODO:Rosetta")
class CatalogueSearchLongFilterChooserAPIIntegrationTest(SearchViewTestCase):
    test_url = reverse_lazy(
        "search-catalogue-long-filter-chooser", kwargs={"field_name": "collection"}
    )

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get(self.test_url)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                f"{settings.CLIENT_BASE_URL}/search"
                "?stream=evidential"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=collection%3A100"
                "&filterAggregations=group%3Atna"
                "&from=0"
                "&size=20"
            ),
        )


@unittest.skip("TODO:Rosetta")
class TestDataLayerSearchViews(WagtailTestUtils, TestCase):
    def assertDataLayerEquals(
        self,
        path: str,
        query_data: Dict[str, Any],
        api_resonse_path: str,
        expected: Dict[str, Any],
    ):
        # Read the API response content into a variable
        with open(api_resonse_path, "r") as f:
            json = json_module.loads(f.read())

        # Ensure API search requests return pre-defined responses
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json=json,
        )

        # Make a GET request to the provided `path` with the supplied `query_data`
        response = self.client.get(path, data=query_data)

        # Ensure the view's get_datalayer_data() method returns the expected value
        request = response.context["request"]
        self.maxDiff = None
        self.assertEqual(
            response.context["view"].get_datalayer_data(request),
            expected,
        )

    @responses.activate
    def test_datalayer_landing_search(self):
        self.assertDataLayerEquals(
            path=reverse("search"),
            query_data={},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/landing_search.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "SearchLandingView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "",
                "customDimension9": "",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 0,
                "customMetric2": 0,
            },
        )

    @responses.activate
    def test_datalayer_catalogue_search_tna(self):
        self.assertDataLayerEquals(
            path=reverse("search-catalogue"),
            query_data={},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_tna.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "CatalogueSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Catalogue results: tna",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 10000,
                "customMetric2": 0,
            },
        )

    @responses.activate
    def test_datalayer_catalogue_search_tna_query(self):
        self.assertDataLayerEquals(
            path=reverse("search-catalogue"),
            query_data={"q": "test search term", "group": "tna"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_tna_query.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "CatalogueSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Catalogue results: tna",
                "customDimension9": "test search term",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 7,
                "customMetric2": 0,
            },
        )

    @responses.activate
    def test_datalayer_catalogue_filtered_search_tna(self):
        self.assertDataLayerEquals(
            path=reverse("search-catalogue"),
            query_data={"collection": "ZOS", "level": "Sub-sub-series", "group": "tna"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_filtered_search_tna.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "CatalogueSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Catalogue results: tna",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 6,
                "customMetric2": 2,
            },
        )

    @responses.activate
    def test_datalayer_catalogue_search_nontna(self):
        self.assertDataLayerEquals(
            path=reverse("search-catalogue"),
            query_data={"group": "nonTna"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_nontna.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "CatalogueSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Catalogue results: nonTna",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 10000,
                "customMetric2": 0,
            },
        )
