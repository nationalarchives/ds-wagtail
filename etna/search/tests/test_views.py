import json as json_module

from typing import Any

from django.conf import settings
from django.http import HttpResponse
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse_lazy

from wagtail.tests.utils import WagtailTestUtils

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

    def get_url(self, url: str, **data: Any) -> HttpResponse:
        return self.client.get(url, data=data)


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
                data = {field_name: value}
                response = self.get_url(self.test_url, **data)
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
        self.get_url(self.test_url)

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
        self.get_url(self.test_url)

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
        self.get_url(self.test_url)

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
        self.get_url(self.test_url, q="query")

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
            sub_heading="Sub heading",
            slug="insight-pages",
        )
        home.add_child(instance=article_index_page)
        article_page = ArticlePage(
            title="William Shakespeare", sub_heading="Sub heading"
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

    def get_url(self, url: str, **data: Any) -> HttpResponse:
        return self.client.get(url, data=data)

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.get_url(self.test_url, group="insight")

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
        response = self.get_url(self.test_url, group="insight")
        self.assertTemplateUsed(response, "search/website_search.html")

    @responses.activate
    def test_current_bucket(self):
        response = self.get_url(self.test_url, group="insight")

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
        response = self.get_url(self.test_url, group="insight")
        self.assertIsInstance(
            response.context_data["page"].object_list[0]["source_page"], ArticlePage
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
            title="Explore the collection", sub_heading="Sub Heading"
        )
        home_page.add_child(instance=explorer_index_page)

        time_period_explorer_index_page = TimePeriodExplorerIndexPage(
            title="Explore by time period", sub_heading="Sub Heading"
        )
        explorer_index_page.add_child(instance=time_period_explorer_index_page)

        time_period_explorer_page = TimePeriodExplorerPage(
            title="Early modern",
            sub_heading="Sub Heading",
            start_year="1485",
            end_year="1714",
        )
        time_period_explorer_index_page.add_child(instance=time_period_explorer_page)

        results_page = ResultsPage(
            title="Shakespeare", introduction="Introduction", sub_heading="Sub Heading"
        )
        time_period_explorer_page.add_child(instance=results_page)

        topic_explorer_index_page = TopicExplorerIndexPage(
            title="Explore by topic", sub_heading="Sub Heading"
        )
        explorer_index_page.add_child(instance=topic_explorer_index_page)

        topic_explorer_page = TopicExplorerPage(
            title="Agriculture and Environment", sub_heading="Sub Heading"
        )
        topic_explorer_index_page.add_child(instance=topic_explorer_page)

        results_page = ResultsPage(
            title="Farm Survey", introduction="Introduction", sub_heading="Sub Heading"
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

    def get_url(self, url: str, **data: Any) -> HttpResponse:
        return self.client.get(url, data=data)

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.get_url(self.test_url, group="highlight")

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
        response = self.get_url(self.test_url, group="highlight")
        self.assertTemplateUsed(response, "search/website_search.html")

    @responses.activate
    def test_current_bucket(self):
        response = self.get_url(self.test_url, group="highlight")

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
        response = self.get_url(self.test_url, group="highlight")
        self.assertIsInstance(
            response.context_data["page"].object_list[0]["source_page"], ResultsPage
        )
        self.assertIsInstance(
            response.context_data["page"].object_list[1]["source_page"], ResultsPage
        )


class TestDataLayerSearchViews(WagtailTestUtils, TestCase):
    @responses.activate
    def test_datalayer_landing_search(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/landing_search.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/")

        self.assertTemplateUsed(response, "search/search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "SearchLandingView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "", "customDimension9": "", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 0, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_featured_search(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/featured_search.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/searchAll",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/featured/")

        self.assertTemplateUsed(response, "search/featured_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "FeaturedSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "All results: none", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 10001, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_featured_search_query(self):
        path = (
            f"{settings.BASE_DIR}/etna/search/tests/fixtures/featured_search_query.json"
        )
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/searchAll",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/featured/?q=test+search+term")

        self.assertTemplateUsed(response, "search/featured_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "FeaturedSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "All results: none", "customDimension9": "test search term", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 11, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_catalogue_search_tna(self):
        path = (
            f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_tna.json"
        )
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/catalogue/")

        self.assertTemplateUsed(response, "search/catalogue_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "CatalogueSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Catalogue results: tna", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 10001, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_catalogue_search_tna_query(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_tna_query.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/catalogue/?q=test+search+term&group=tna")

        self.assertTemplateUsed(response, "search/catalogue_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "CatalogueSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Catalogue results: tna", "customDimension9": "test search term", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 7, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_catalogue_filtered_search_tna(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_filtered_search_tna.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get(
            "/search/catalogue/?collection=ZOS&level=Sub-sub-series&group=tna"
        )

        self.assertTemplateUsed(response, "search/catalogue_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "CatalogueSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Catalogue results: tna", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 6, "customMetric2": 2}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_catalogue_search_digitised(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_digitised.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/catalogue/?group=digitised")

        self.assertTemplateUsed(response, "search/catalogue_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "CatalogueSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Catalogue results: digitised", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 10001, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_catalogue_search_nontna(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_nontna.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/catalogue/?group=nonTna")

        self.assertTemplateUsed(response, "search/catalogue_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "CatalogueSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Catalogue results: nonTna", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 10001, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_catalogue_search_creator(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_creator.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/catalogue/?group=creator")

        self.assertTemplateUsed(response, "search/catalogue_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "CatalogueSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Catalogue results: creator", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 0, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_catalogue_search_archive(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/catalogue_search_archive.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/catalogue/?group=archive")

        self.assertTemplateUsed(response, "search/catalogue_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "CatalogueSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Catalogue results: archive", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 3477, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_website_filtered_search_blog(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_filtered_search_blog.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/website/?topic=Conservation&group=blog")

        self.assertTemplateUsed(response, "search/website_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "WebsiteSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Website results: blog", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 47, "customMetric2": 1}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_website_search_blog_query(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_blog_query.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/website/?q=test&group=blog")

        self.assertTemplateUsed(response, "search/website_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "WebsiteSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Website results: blog", "customDimension9": "test", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 8, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_website_search_blog(self):
        path = (
            f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_blog.json"
        )
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/website/?group=blog")

        self.assertTemplateUsed(response, "search/website_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "WebsiteSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Website results: blog", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 1653, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_website_search_researchguide(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_researchguide.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/website/?group=researchGuide")

        self.assertTemplateUsed(response, "search/website_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "WebsiteSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Website results: researchGuide", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 359, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_website_search_article(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_insight2.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/website/?group=insight")

        self.assertTemplateUsed(response, "search/website_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "WebsiteSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Website results: insight", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 9, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_website_search_highlight(self):
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_highlight2.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/website/?group=highlight")

        self.assertTemplateUsed(response, "search/website_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "WebsiteSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Website results: highlight", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 67, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_website_search_audio(self):
        path = (
            f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_audio.json"
        )
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json_module.loads(f.read()),
            )

        response = self.client.get("/search/website/?group=audio")

        self.assertTemplateUsed(response, "search/website_search.html")

        html_decoded_response = response.content.decode("utf8")
        desired_datalayer_script_tag = """<script id="gtmDatalayer" type="application/json">{"contentGroup1": "Search", "customDimension1": "offsite", "customDimension2": "", "customDimension3": "WebsiteSearchView", "customDimension4": "", "customDimension5": "", "customDimension6": "", "customDimension7": "", "customDimension8": "Website results: audio", "customDimension9": "*", "customDimension10": "", "customDimension11": "", "customDimension12": "", "customDimension13": "", "customDimension14": "", "customDimension15": "", "customDimension16": "", "customDimension17": "", "customMetric1": 644, "customMetric2": 0}</script>"""
        self.assertIn(desired_datalayer_script_tag, html_decoded_response)

    @responses.activate
    def test_datalayer_website_search_video(self):
        path = (
            f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_video.json"
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
