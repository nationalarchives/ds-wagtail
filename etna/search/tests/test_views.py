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


class SelectedFiltersTest(SimpleTestCase):
    def get_result(self, form):
        return CatalogueSearchView().get_selected_filters(form)

    def test_with_valid_filter_values(self):
        self.maxDiff = None
        form = CatalogueSearchForm(
            {
                "group": "tna",
                # TODO: Keep, not in scope for Ohos-Etna at this time
                # "topic": ["topic-one"],
                # "level": ["Division"],
                "collection": [
                    "WO",
                    "AK",
                    "Biography of Women Who Made Milton Keynes (Digital Document)",
                ],
                # TODO: Keep, not in scope for Ohos-Etna at this time
                # "country": ["England", "Yorkshire, North Riding"],
                # "location": ["Australia", "United States of America"],
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
                    (
                        "Biography of Women Who Made Milton Keynes (Digital Document)",
                        "Biography of Women Who Made Milton Keynes (Digital Document)",
                    ),
                ],
                # TODO: Keep, not in scope for Ohos-Etna at this time
                # "level": [("Division", "Division")],
                # "topic": [("topic-one", "topic-one")],
                # "country": [
                #     ("England", "England"),
                #     ("Yorkshire, North Riding", "Yorkshire, North Riding"),
                # ],
                # "location": [
                #     ("Australia", "Australia"),
                #     ("United States of America", "United States of America"),
                # ],
            },
        )

    @unittest.skip("# TODO: Keep, not in scope for Ohos-Etna at this time")
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
                {"value": "topic-one", "doc_count": 10},
            ]
        )
        self.assertEqual(topic_field.choices, [("topic-one", "topic-one (10)")])

        # Update level field choices to include counts on labels
        level_field.update_choices(
            [
                {
                    "value": "Division",
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

    @unittest.skip("# TODO: Keep, not in scope for Ohos-Etna at this time")
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

    @unittest.skip("TODO: Keep, not in scope for Ohos-Etna at this time")
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


class CatalogueSearchAPIIntegrationTest(SearchViewTestCase):
    test_url = reverse_lazy("search-catalogue")

    @responses.activate
    @override_settings(
        FEATURE_GEO_LAT=f"{12345.6789}",
        FEATURE_GEO_LON=f"{-54321.12345}",
        FEATURE_GEO_ZOOM=f"{3}",
    )
    def test_context_data_map_view(self):
        self.test_url = f"{self.test_url}?vis_view=map"
        response = self.client.get(self.test_url)
        self.assertEqual(
            response.context.get("default_geo_data"),
            {
                "lat": settings.FEATURE_GEO_LAT,
                "lon": settings.FEATURE_GEO_LON,
                "zoom": settings.FEATURE_GEO_ZOOM,
            },
        )

    @responses.activate
    @override_settings(
        FEATURE_GEO_LAT=f"{12345.6789}",
        FEATURE_GEO_LON=f"{-54321.12345}",
        FEATURE_GEO_ZOOM=f"{3}",
    )
    def test_context_data_list_view(self):
        self.test_url = f"{self.test_url}?vis_view=list"
        response = self.client.get(self.test_url)
        self.assertEqual(
            response.context.get("list_view_url"),
            "/search/catalogue/?group=community&vis_view=list",
        )
        self.assertEqual(
            response.context.get("map_view_url"),
            "/search/catalogue/?group=community&vis_view=map",
        )
        self.assertEqual(
            response.context.get("timeline_view_url"),
            "/search/catalogue/?group=community&vis_view=timeline&timeline_type=century",
        )
        self.assertEqual(
            response.context.get("tag_view_url"),
            "/search/catalogue/?group=community&vis_view=tag",
        )

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get(self.test_url)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                f"{settings.CLIENT_BASE_URL}/search"
                "?aggs=community"
                "&filter=group%3Acommunity"
                "&sort="
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
    selected_bucket_html = (
        '<option value="{group}" selected >{bucket} ({count})</option>'
    )
    unselected_bucket_html = '<option value="{group}"  >{bucket} ({count})</option>'

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

    def assertSelectedBucketRendered(self, group, count, bucket, response):
        self.assertIn(
            self.selected_bucket_html.format(group=group, count=count, bucket=bucket),
            response,
        )

    def assertUnSelectedBucketRendered(self, group, count, bucket, response):
        self.assertIn(
            self.unselected_bucket_html.format(group=group, count=count, bucket=bucket),
            response,
        )

    def assertShowingRendered(self, text, response):
        self.assertIn(text, response)


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
            data={
                "q": "japan",
                "covering_date_from_0": "01",
                "covering_date_from_1": "01",
                "covering_date_from_2": "5000",
            },
        )
        content = str(response.content)

        # SHOULD see
        self.assertBucketLinksRendered(content)
        # self.assertSearchWithinOptionRendered(content) # TODO: Rosetta - not for OHOS
        self.assertSortOptionsRendered(content)
        self.assertNoResultsMessagingRendered(content)
        self.assertFilterOptionsRendered(content)

        # SHOULD NOT see
        self.assertResultsNotRendered(content)
        self.assertSearchWithinOptionNotRendered(content)  # For OHOS

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
        - Buckets rendered

        They SHOULD NOT see:
        -  A "No results" message.
        """

        self.patch_search_endpoint("catalogue_search_refined_with_matches.json")
        response = self.client.get(
            self.test_url,
            data={
                "q": "biography",
                "group": "community",
                "collection": "Biography of Women Who Made Milton Keynes (Digital Document)",
            },
        )
        content = str(response.content)

        # SHOULD see
        self.assertBucketLinksRendered(content)
        # self.assertSearchWithinOptionRendered(content) # TODO:Rosetta - not for OHOS
        self.assertSortOptionsRendered(content)
        self.assertFilterOptionsRendered(content)
        self.assertResultsRendered(content)
        self.assertSelectedBucketRendered(
            "community", "204", "Results from community collections", content
        )
        self.assertUnSelectedBucketRendered(
            "tna", "558", "Results from The National Archives", content
        )
        self.assertUnSelectedBucketRendered(
            "nonTna", "6,393", "Results from other archives", content
        )

        # SHOULD NOT see
        self.assertNoResultsMessagingNotRendered(content)
        self.assertSearchWithinOptionNotRendered(content)  # For OHOS

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
        self.patch_search_endpoint(
            "catalogue_search_with_multiple_filters_community.json"
        )

        expected_url = "/search/catalogue/?q=parish&group=community&collection=SWOP&collection=People%27s+Collection+Wales"

        response = self.client.get(
            self.test_url,
            data={
                "q": "parish",
                "group": "community",
                "collection": [
                    "SWOP",
                    "People's Collection Wales",
                ],
            },
        )
        session = self.client.session
        content = str(response.content)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(session.get("back_to_search_url"), expected_url)

        self.assertIn('<input type="checkbox" name="collection" value="SWOP"', content)
        self.assertIn(
            '<input type="checkbox" name="collection" value="People&#x27;s Collection Wales"',
            content,
        )
        self.assertSelectedBucketRendered(
            "community", "5,415", "Results from community collections", content
        )
        self.assertUnSelectedBucketRendered(
            "tna", "286,707", "Results from The National Archives", content
        )
        self.assertUnSelectedBucketRendered(
            "nonTna", "928,752", "Results from other archives", content
        )
        self.assertShowingRendered("(of 5,345) results", content)
        self.assertShowingRendered('for "parish"', content)
        self.assertShowingRendered(
            'in "<span id="analytics-current-bucket" data-current-bucket="Results from community collections">Results from community collections</span>"',
            content,
        )

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
            # ("opening_start_date", "opening_end_date"), # TODO:Rosetta
            ("covering_date_from", "covering_date_to"),
        ):
            response = self.client.get(
                self.test_url,
                data={
                    "group": "community",
                    f"{from_date_field}_0": "01",
                    f"{from_date_field}_1": "01",
                    f"{from_date_field}_2": "2000",
                    f"{to_date_field}_0": "01",
                    f"{to_date_field}_1": "01",
                    f"{to_date_field}_2": "1999",
                    "q": "london",
                    # "filter_keyword": "kew", # TODO:Rosetta
                },
            )
            content = str(response.content)

            # SHOULD see
            self.assertNoResultsMessagingRendered(content)
            self.assertIn("<li>Use different spellings or search terms</li>", content)
            # self.assertSearchWithinOptionRendered(content) # TODO:Rosetta
            self.assertIn(from_date_field, response.context["form"].errors)
            self.assertIn(
                "<li>This date must be earlier than or equal to the &#x27;to&#x27; date.</li>",
                content,
            )

    @responses.activate
    def test_search_results_having_enrichment_tags(self):

        self.patch_search_endpoint("catalogue_search_having_enrichment_tags.json")

        expected_url = "/search/catalogue/?q=swop-94010&group=community&collection=SWOP&vis_view=list"

        response = self.client.get(
            self.test_url,
            data={
                "q": "swop-94010",
                "group": "community",
                "collection": [
                    "SWOP",
                ],
                "vis_view": "list",
            },
        )
        session = self.client.session
        content = str(response.content)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(session.get("back_to_search_url"), expected_url)

        self.assertIn('<span class="ohos-tag ohos-tag--location">', content)
        self.assertIn('<span class="ohos-tag__inner">Town Hall</span>', content)
        self.assertIn('<span class="ohos-tag ohos-tag--person">', content)
        self.assertIn('<span class="ohos-tag__inner">Ray Whitney</span>', content)
        self.assertIn('<span class="ohos-tag ohos-tag--organisation">', content)
        self.assertIn('<span class="ohos-tag__inner">H.W.Society</span>', content)


@unittest.skip("TODO: Keep, not in scope for Ohos-Etna at this time")
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


@unittest.skip("TODO: Keep, not in scope for Ohos-Etna at this time")
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
