import json as json_module
import unittest

from typing import Any, Dict

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse, reverse_lazy

from wagtail.test.utils import WagtailTestUtils

import responses

from etna.ciim.constants import Bucket, BucketList
from etna.core.test_utils import prevent_request_warnings

from ...articles.models import ArticleIndexPage, ArticlePage
from ...ciim.tests.factories import create_response, create_search_response
from ...home.models import HomePage
from ..forms import CatalogueSearchForm
from ..views import CatalogueSearchView


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class SearchViewTestCase(WagtailTestUtils, TestCase):
    maxDiff = None

    def setUp(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json={
                "responses": [
                    create_response(),
                    create_response(),
                ]
            },
        )
        responses.add(
            responses.GET,
            "https://kong.test/data/searchAll",
            json={
                "responses": [
                    create_response(),
                    create_response(),
                    create_response(),
                    create_response(),
                    create_response(),
                    create_response(),
                ]
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
            ("sort_by", "baz"),
            ("sort_order", "foo"),
            ("display", "foo"),
        ]:
            with self.subTest(f"{field_name} = {value}"):
                response = self.client.get(self.test_url, data={field_name: value})
                self.assertEqual(response.status_code, 400)


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


class CatalogueSearchAPIIntegrationTest(SearchViewTestCase):
    test_url = reverse_lazy("search-catalogue")

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get(self.test_url)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=evidential"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=collection%3A10"
                "&aggregations=level%3A10"
                "&aggregations=topic%3A10"
                "&aggregations=closure%3A10"
                "&aggregations=heldBy%3A10"
                "&aggregations=catalogueSource%3A10"
                "&aggregations=group%3A30"
                "&aggregations=type%3A10"
                "&filterAggregations=group%3Atna"
                "&from=0"
                "&size=20"
            ),
        )


@override_settings(KONG_CLIENT_BASE_URL="https://kong.test")
class EndToEndSearchTestCase(TestCase):
    # The following HTML snippets must be updated to reflect any future HTML changes
    results_html = '<ul class="search-results__list" id="analytics-results-list">'
    no_results_messaging_html = '<div class="no-results">'
    bucket_links_html = (
        '<ul class="search-buckets__list" data-id="search-buckets-list">'
    )
    current_bucket_description_html = (
        '<p class="search-results__explainer search-results__explainer--bucket">'
    )
    search_within_option_html = '<label for="id_filter_keyword" class="search-filters__label--block">Search within results:</label>'
    sort_order_options_html = '<label for="id_sort_by">Sort by</label>'
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
        self.patch_api_endpoint("https://kong.test/data/search", fixture_path)

    def assertNoResultsMessagingRendered(self, response):
        self.assertIn(self.no_results_messaging_html, response)

    def assertNoResultsMessagingNotRendered(self, response):
        self.assertNotIn(self.no_results_messaging_html, response)

    def assertBucketLinksRendered(self, response):
        self.assertIn(self.bucket_links_html, response)

    def assertBucketLinksNotRendered(self, response):
        self.assertNotIn(self.bucket_links_html, response)

    def assertCurrentBucketDescriptionRendered(self, response):
        self.assertIn(self.current_bucket_description_html, response)

    def assertCurrentBucketDescriptionNotRendered(self, response):
        self.assertNotIn(self.current_bucket_description_html, response)

    def assertSearchWithinOptionRendered(self, response):
        self.assertIn(self.search_within_option_html, response)

    def assertSearchWithinOptionNotRendered(self, response):
        self.assertNotIn(self.search_within_option_html, response)

    def assertSortOrderOptionsRendered(self, response):
        self.assertIn(self.sort_order_options_html, response)

    def assertSortOrderOptionsNotRendered(self, response):
        self.assertNotIn(self.sort_order_options_html, response)

    def assertFilterOptionsRendered(self, response):
        self.assertIn(self.filter_options_html, response)

    def assertFilterOptionsNotRendered(self, response):
        self.assertNotIn(self.filter_options_html, response)

    def assertResultsRendered(self, response):
        self.assertIn(self.results_html, response)

    def assertResultsNotRendered(self, response):
        self.assertNotIn(self.results_html, response)


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
        - A description of the current bucket
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
        self.assertCurrentBucketDescriptionNotRendered(content)
        self.assertSearchWithinOptionNotRendered(content)
        self.assertSortOrderOptionsNotRendered(content)
        self.assertFilterOptionsNotRendered(content)
        self.assertResultsNotRendered(content)

    @responses.activate
    def test_no_matches_for_the_current_bucket(self):
        """
        When a user searches for something that has results for SOME buckets,
        but they are currently viewing a bucket with no results:

        They SHOULD see:
        - Names, result counts and links for all buckets
        - A "No results" message.

        They SHOULD NOT see:
        - A description of the current bucket
        - A "Search within these results" option
        - Options to change sort order and display style of results
        - Filter options to refine the search
        - Search results
        """

        self.patch_search_endpoint("catalogue_search_with_some_empty_buckets.json")
        response = self.client.get(
            self.test_url, data={"q": "snub", "group": "creator"}
        )
        content = str(response.content)

        # SHOULD see
        self.assertBucketLinksRendered(content)
        self.assertNoResultsMessagingRendered(content)

        # SHOULD NOT see
        self.assertCurrentBucketDescriptionNotRendered(content)
        self.assertSearchWithinOptionNotRendered(content)
        self.assertSortOrderOptionsNotRendered(content)
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
        - A description of the current bucket
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
        self.assertCurrentBucketDescriptionRendered(content)
        self.assertSearchWithinOptionRendered(content)
        self.assertSortOrderOptionsRendered(content)
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
        - A description of the current bucket
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
        self.assertCurrentBucketDescriptionRendered(content)
        self.assertSearchWithinOptionRendered(content)
        self.assertSortOrderOptionsRendered(content)
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
        - Error message in area of Record opening date
        """
        response = self.client.get(
            self.test_url,
            data={
                "group": "tna",
                "opening_start_date_2": "2000",
                "opening_end_date_2": "1900",
                "q": "london",
                "filter_keyword": "kew",
            },
        )
        content = str(response.content)

        # SHOULD see
        self.assertNoResultsMessagingRendered(content)
        self.assertIn(
            "<li>Try removing any filters that you may have applied</li>", content
        )
        self.assertSearchWithinOptionRendered(content)
        self.assertIn(
            "<li>There is a problem. Start date cannot be after end date.</li>", content
        )


class WebsiteSearchEndToEndTest(EndToEndSearchTestCase):
    test_url = reverse_lazy("search-website")

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
        self.patch_search_endpoint("website_search_no_results.json")
        response = self.client.get(self.test_url, data={"q": "qwerty"})
        content = str(response.content)

        # SHOULD see
        self.assertNoResultsMessagingRendered(content)

        # SHOULD NOT see
        self.assertBucketLinksNotRendered(content)
        self.assertSearchWithinOptionNotRendered(content)
        self.assertSortOrderOptionsNotRendered(content)
        self.assertFilterOptionsNotRendered(content)
        self.assertResultsNotRendered(content)

    @responses.activate
    def test_no_matches_for_the_current_bucket(self):
        """
        When a user searches for something that has results for SOME buckets,
        but they are currently viewing a bucket with no results:

        They SHOULD see:
        - Names, result counts and links for all buckets
        - A "No results" message.

        They SHOULD NOT see:
        - A "Search within these results" option
        - Options to change sort order and display style of results
        - Filter options to refine the search
        - Search results
        """
        self.patch_search_endpoint("website_search_with_some_empty_buckets.json")
        response = self.client.get(self.test_url, data={"q": "japan", "group": "audio"})
        content = str(response.content)

        # SHOULD see
        self.assertBucketLinksRendered(content)
        self.assertNoResultsMessagingRendered(content)

        # SHOULD NOT see
        self.assertSearchWithinOptionNotRendered(content)
        self.assertSortOrderOptionsNotRendered(content)
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

        self.patch_search_endpoint("website_search_empty_after_refining.json")
        response = self.client.get(
            self.test_url,
            data={"q": "japan", "group": "blog", "filter_keyword": "qwerty"},
        )
        content = str(response.content)

        # SHOULD see
        self.assertBucketLinksRendered(content)
        self.assertSearchWithinOptionRendered(content)
        self.assertSortOrderOptionsRendered(content)
        self.assertFilterOptionsRendered(content)
        self.assertNoResultsMessagingRendered(content)

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
        self.patch_search_endpoint("website_search_refined_with_matches.json")
        response = self.client.get(
            self.test_url,
            data={
                "q": "japan",
                "group": "blog",
                "topic": "East India Company",
            },
        )
        content = str(response.content)

        # SHOULD see
        self.assertBucketLinksRendered(content)
        self.assertSearchWithinOptionRendered(content)
        self.assertSortOrderOptionsRendered(content)
        self.assertFilterOptionsRendered(content)
        self.assertResultsRendered(content)

        # SHOULD NOT see
        self.assertNoResultsMessagingNotRendered(content)


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
                "https://kong.test/data/search"
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


class FeaturedSearchAPIIntegrationTest(SearchViewTestCase):
    test_url = reverse_lazy("search-featured")

    @responses.activate
    def test_accessing_page_with_no_params_performs_search(self):
        self.client.get(self.test_url)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/searchAll"
                "?filterAggregations=group%3Atna"
                "&filterAggregations=group%3AnonTna"
                "&filterAggregations=group%3Acreator"
                "&filterAggregations=group%3Ablog"
                "&filterAggregations=group%3AresearchGuide"
                "&filterAggregations=group%3Ainsight"
                "&size=3"
            ),
        )

    @responses.activate
    def test_search_with_query(self):
        """
        Test covers create session info for Featured search with query.
        """
        expected_url = "/search/featured/?q=query"
        self.client.get(self.test_url, data={"q": "query"})
        session = self.client.session

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/searchAll"
                "?q=query"
                "&filterAggregations=group%3Atna"
                "&filterAggregations=group%3AnonTna"
                "&filterAggregations=group%3Acreator"
                "&filterAggregations=group%3Ablog"
                "&filterAggregations=group%3AresearchGuide"
                "&filterAggregations=group%3Ainsight"
                "&size=3"
            ),
        )
        self.assertEqual(session.get("back_to_search_url"), expected_url)


class WebsiteSearchAPIIntegrationTest(SearchViewTestCase):
    test_url = reverse_lazy("search-website")

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get(self.test_url)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=interpretive"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=collection%3A10"
                "&aggregations=level%3A10"
                "&aggregations=topic%3A10"
                "&aggregations=closure%3A10"
                "&aggregations=heldBy%3A10"
                "&aggregations=catalogueSource%3A10"
                "&aggregations=group%3A30"
                "&aggregations=type%3A10"
                "&filterAggregations=group%3Ablog"
                "&from=0"
                "&size=20"
            ),
        )


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
)
class WebsiteSearchArticleTest(WagtailTestUtils, TestCase):
    maxDiff = None
    test_url = reverse_lazy("search-website")

    def setUp(self):
        super().setUp()

        # create article page object
        home = HomePage.objects.get()
        # explict slug so that title does not default to slug
        article_index_page = ArticleIndexPage(
            title="Insight Pages",
            intro="test",
            teaser_text="test",
            slug="insight-pages",
        )
        home.add_child(instance=article_index_page)
        article_page = ArticlePage(
            title="William Shakespeare", intro="test", teaser_text="test"
        )
        article_index_page.add_child(instance=article_page)

        # create article page response in sourceUrl
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_insight.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get(self.test_url, data={"group": "insight"})

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=interpretive"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=collection%3A10"
                "&aggregations=level%3A10"
                "&aggregations=topic%3A10"
                "&aggregations=closure%3A10"
                "&aggregations=heldBy%3A10"
                "&aggregations=catalogueSource%3A10"
                "&aggregations=group%3A30"
                "&aggregations=type%3A10"
                "&filterAggregations=group%3Ainsight"
                "&from=0"
                "&size=20"
            ),
        )

    @responses.activate
    def test_template_used(self):
        response = self.client.get(self.test_url, data={"group": "insight"})
        self.assertTemplateUsed(response, "search/website_search.html")

    @responses.activate
    def test_current_bucket(self):
        response = self.client.get(self.test_url, data={"group": "insight"})

        # insight is current, others are not
        expected_bucket_list = BucketList(
            [
                Bucket(
                    key="blog",
                    label="Blog posts",
                    result_count=8,
                    is_current=False,
                    results=None,
                ),
                Bucket(
                    key="researchGuide",
                    label="Research Guides",
                    result_count=1,
                    is_current=False,
                    results=None,
                ),
                Bucket(
                    key="insight",
                    label="Insights",
                    result_count=1,
                    is_current=True,
                    results=None,
                ),
                # TODO: Restore when we are succesfully indexing new highlight pages
                # Bucket(
                #   key="highlight",
                #   label="Highlights",
                #   result_count=1,
                #   is_current=True,
                #   results=None,
                # ),
                Bucket(
                    key="audio",
                    label="Audio",
                    result_count=0,
                    is_current=False,
                    results=None,
                ),
                Bucket(
                    key="video",
                    label="Video",
                    result_count=0,
                    is_current=False,
                    results=None,
                ),
            ]
        )
        self.assertEqual(response.context_data["buckets"], expected_bucket_list)

    @responses.activate
    def test_page_instance_added_for_source_url(self):
        response = self.client.get(self.test_url, data={"group": "insight"})
        self.assertIsInstance(
            response.context_data["page"].object_list[0].source_page, ArticlePage
        )


@unittest.skip("Highlights bucket to be re-instated at a later date")
@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
)
class WebsiteSearchHighlightTest(WagtailTestUtils, TestCase):
    maxDiff = None
    test_url = reverse_lazy("search-website")

    def setUp(self):
        super().setUp()

        # create article page response in sourceUrl
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_highlight.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get(self.test_url, data={"group": "highlight"})

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=interpretive"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=collection%3A10"
                "&aggregations=level%3A10"
                "&aggregations=topic%3A10"
                "&aggregations=closure%3A10"
                "&aggregations=heldBy%3A10"
                "&aggregations=catalogueSource%3A10"
                "&aggregations=group%3A30"
                "&aggregations=type%3A10"
                "&filterAggregations=group%3Ahighlight"
                "&from=0"
                "&size=20"
            ),
        )

    @responses.activate
    def test_template_used(self):
        response = self.client.get(self.test_url, data={"group": "highlight"})
        self.assertTemplateUsed(response, "search/website_search.html")

    @responses.activate
    def test_current_bucket(self):
        response = self.client.get(self.test_url, data={"group": "highlight"})

        # highlight is current, others are not
        expected_bucket_list = BucketList(
            [
                Bucket(
                    key="blog",
                    label="Blog posts",
                    result_count=16,
                    is_current=False,
                    results=None,
                ),
                Bucket(
                    key="researchGuide",
                    label="Research Guides",
                    result_count=1,
                    is_current=False,
                    results=None,
                ),
                Bucket(
                    key="insight",
                    label="Insights",
                    result_count=1,
                    is_current=False,
                    results=None,
                ),
                # TODO: Restore when we are succesfully indexing new highlight pages
                # Bucket(
                #   key="highlight",
                #   label="Highlights",
                #   result_count=2,
                #   is_current=True,
                #   results=None,
                # ),
                Bucket(
                    key="audio",
                    label="Audio",
                    result_count=3,
                    is_current=False,
                    results=None,
                ),
                Bucket(
                    key="video",
                    label="Video",
                    result_count=0,
                    is_current=False,
                    results=None,
                ),
            ]
        )
        self.assertEqual(response.context_data["buckets"], expected_bucket_list)


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
            "https://kong.test/data/search",
            json=json,
        )
        responses.add(
            responses.GET,
            "https://kong.test/data/searchAll",
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
    def test_datalayer_featured_search(self):
        self.assertDataLayerEquals(
            path=reverse("search-featured"),
            query_data={},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/featured_search.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "FeaturedSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "All results: none",
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
    def test_datalayer_featured_search_query(self):
        self.assertDataLayerEquals(
            path=reverse("search-featured"),
            query_data={"q": "test search term"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/featured_search_query.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "FeaturedSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "All results: none",
                "customDimension9": "test search term",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 11,
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
    def test_datalayer_catalogue_search_digitised(self):
        self.assertDataLayerEquals(
            path=reverse("search-catalogue"),
            query_data={"group": "digitised"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_digitised.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "CatalogueSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Catalogue results: digitised",
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

    @responses.activate
    def test_datalayer_catalogue_search_creator(self):
        self.assertDataLayerEquals(
            path=reverse("search-catalogue"),
            query_data={"group": "creator"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_creator.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "CatalogueSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Catalogue results: creator",
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
    def test_datalayer_catalogue_search_archive(self):
        self.assertDataLayerEquals(
            path=reverse("search-catalogue"),
            query_data={"group": "archive"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_archive.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "CatalogueSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Catalogue results: archive",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 3477,
                "customMetric2": 0,
            },
        )

    @responses.activate
    def test_datalayer_website_filtered_search_blog(self):
        self.assertDataLayerEquals(
            path=reverse("search-website"),
            query_data={"group": "blog", "topic": "Conservation"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_filtered_search_blog.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "WebsiteSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Website results: blog",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 47,
                "customMetric2": 1,
            },
        )

    @responses.activate
    def test_datalayer_website_search_blog_query(self):
        self.assertDataLayerEquals(
            path=reverse("search-website"),
            query_data={"q": "test", "group": "blog"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_blog_query.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "WebsiteSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Website results: blog",
                "customDimension9": "test",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 8,
                "customMetric2": 0,
            },
        )

    @responses.activate
    def test_datalayer_website_search_blog(self):
        self.assertDataLayerEquals(
            path=reverse("search-website"),
            query_data={"group": "blog"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_blog.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "WebsiteSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Website results: blog",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 1653,
                "customMetric2": 0,
            },
        )

    @responses.activate
    def test_datalayer_website_search_researchguide(self):
        self.assertDataLayerEquals(
            path=reverse("search-website"),
            query_data={"group": "researchGuide"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_researchguide.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "WebsiteSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Website results: researchGuide",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 359,
                "customMetric2": 0,
            },
        )

    @responses.activate
    def test_datalayer_website_search_article(self):
        self.assertDataLayerEquals(
            path=reverse("search-website"),
            query_data={"group": "insight"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_insight2.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "WebsiteSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Website results: insight",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 9,
                "customMetric2": 0,
            },
        )

    @unittest.skip("Highlights bucket to be re-instated at a later date")
    @responses.activate
    def test_datalayer_website_search_highlight(self):
        self.assertDataLayerEquals(
            path=reverse("search-website"),
            query_data={"group": "highlight"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_highlight2.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "WebsiteSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Website results: highlight",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 67,
                "customMetric2": 0,
            },
        )

    @responses.activate
    def test_datalayer_website_search_audio(self):
        self.assertDataLayerEquals(
            path=reverse("search-website"),
            query_data={"group": "audio"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_audio.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "WebsiteSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Website results: audio",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 644,
                "customMetric2": 0,
            },
        )

    @responses.activate
    def test_datalayer_website_search_video(self):
        self.assertDataLayerEquals(
            path=reverse("search-website"),
            query_data={"group": "video"},
            api_resonse_path=f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_video.json",
            expected={
                "contentGroup1": "Search",
                "customDimension1": "offsite",
                "customDimension2": "",
                "customDimension3": "WebsiteSearchView",
                "customDimension4": "",
                "customDimension5": "",
                "customDimension6": "",
                "customDimension7": "",
                "customDimension8": "Website results: video",
                "customDimension9": "*",
                "customDimension10": "",
                "customDimension11": "",
                "customDimension12": "",
                "customDimension13": "",
                "customDimension14": "",
                "customDimension15": "",
                "customDimension16": "",
                "customDimension17": "",
                "customMetric1": 348,
                "customMetric2": 0,
            },
        )


class WebsiteSearchLongFilterChooserAPIIntegrationTest(SearchViewTestCase):
    test_url = reverse_lazy(
        "search-website-long-filter-chooser", kwargs={"field_name": "topic"}
    )

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get(self.test_url)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=interpretive"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=topic%3A100"
                "&filterAggregations=group%3Ablog"
                "&from=0"
                "&size=20"
            ),
        )


class RecordCreatorsTestCase(WagtailTestUtils, TestCase):
    maxDiff = None

    @responses.activate
    def test_record_creators_default_params(self):
        test_url = reverse_lazy(
            "search-catalogue",
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_search_response(),
        )

        self.client.get(test_url, data={"group": "creator"})

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=evidential"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=group%3A30"
                "&aggregations=type%3A10"
                "&aggregations=country%3A10"
                "&filterAggregations=group%3Acreator"
                "&from=0"
                "&size=20"
            ),
        )

    @responses.activate
    def test_record_creators_country_long_filter(self):
        test_url = reverse_lazy(
            "search-catalogue-long-filter-chooser", kwargs={"field_name": "country"}
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_search_response(),
        )

        self.client.get(test_url, data={"group": "creator"})

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=evidential"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=country%3A100"
                "&filterAggregations=group%3Acreator"
                "&from=0"
                "&size=20"
            ),
        )


class ArchiveTestCase(WagtailTestUtils, TestCase):
    maxDiff = None

    @responses.activate
    def test_archive_default_params(self):
        test_url = reverse_lazy(
            "search-catalogue",
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_search_response(),
        )

        self.client.get(test_url, data={"group": "archive"})

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=evidential"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=group%3A30"
                "&aggregations=location%3A10"
                "&filterAggregations=group%3Aarchive"
                "&from=0"
                "&size=20"
            ),
        )

    @responses.activate
    def test_record_creators_country_long_filter(self):
        test_url = reverse_lazy(
            "search-catalogue-long-filter-chooser", kwargs={"field_name": "location"}
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_search_response(),
        )

        self.client.get(test_url, data={"group": "archive"})

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=evidential"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=location%3A100"
                "&filterAggregations=group%3Aarchive"
                "&from=0"
                "&size=20"
            ),
        )
