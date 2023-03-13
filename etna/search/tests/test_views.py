import json as json_module

from typing import Any, Dict

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse, reverse_lazy

from wagtail.test.utils import WagtailTestUtils

import responses

from etna.ciim.constants import Bucket, BucketList
from etna.core.test_utils import prevent_request_warnings

from ...articles.models import ArticleIndexPage, ArticlePage
from ...ciim.tests.factories import create_response
from ...collections.models import (
    ExplorerIndexPage,
    ResultsPage,
    TimePeriodExplorerIndexPage,
    TimePeriodExplorerPage,
    TopicExplorerIndexPage,
    TopicExplorerPage,
)
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
        self.client.get(self.test_url, data={"q": "query"})

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
                Bucket(
                    key="highlight",
                    label="Highlights",
                    result_count=1,
                    is_current=False,
                    results=None,
                ),
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


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
)
class WebsiteSearchHighlightTest(WagtailTestUtils, TestCase):
    maxDiff = None
    test_url = reverse_lazy("search-website")

    def setUp(self):
        super().setUp()

        # create results page object each for Topic and Time
        home_page = HomePage.objects.get()
        explorer_index_page = ExplorerIndexPage(
            title="Explore the collection", intro="test", teaser_text="test"
        )
        home_page.add_child(instance=explorer_index_page)

        time_period_explorer_index_page = TimePeriodExplorerIndexPage(
            title="Explore by time period", intro="test", teaser_text="test"
        )
        explorer_index_page.add_child(instance=time_period_explorer_index_page)

        time_period_explorer_page = TimePeriodExplorerPage(
            title="Early modern",
            intro="test",
            teaser_text="test",
            start_year="1485",
            end_year="1714",
        )
        time_period_explorer_index_page.add_child(instance=time_period_explorer_page)

        results_page = ResultsPage(
            title="Shakespeare",
            introduction="test",
            sub_heading="test",
            teaser_text="test",
        )
        time_period_explorer_page.add_child(instance=results_page)

        topic_explorer_index_page = TopicExplorerIndexPage(
            title="Explore by topic", intro="test", teaser_text="test"
        )
        explorer_index_page.add_child(instance=topic_explorer_index_page)

        topic_explorer_page = TopicExplorerPage(
            title="Agriculture and Environment", intro="test", teaser_text="test"
        )
        topic_explorer_index_page.add_child(instance=topic_explorer_page)

        results_page = ResultsPage(
            title="Farm Survey",
            introduction="test",
            sub_heading="test",
            teaser_text="test",
        )
        topic_explorer_page.add_child(instance=results_page)

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
                Bucket(
                    key="highlight",
                    label="Highlights",
                    result_count=2,
                    is_current=True,
                    results=None,
                ),
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

    @responses.activate
    def test_page_instance_added_for_source_url(self):
        response = self.client.get(self.test_url, data={"group": "highlight"})
        self.assertIsInstance(
            response.context_data["page"].object_list[0].source_page, ResultsPage
        )
        self.assertIsInstance(
            response.context_data["page"].object_list[1].source_page, ResultsPage
        )


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
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/website/?group=video")

        self.assertTemplateUsed(response, "search/website_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "WebsiteSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Website results: video", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 348, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)


class WebsiteSearchLongFilterChooserAPIIntegrationTest(SearchViewTestCase):
    test_url = reverse_lazy(
        "search-website-long-filter-chooser", kwargs={"field_name": "topic"}
    )

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.get_url(self.test_url)

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
