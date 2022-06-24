import json

from typing import Any

from django.conf import settings
from django.http import HttpResponse
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse_lazy

from wagtail.tests.utils import WagtailTestUtils

import responses

from etna.ciim.constants import Bucket, BucketList

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
from ...insights.models import InsightsIndexPage, InsightsPage
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
                "&filterAggregations=group%3Ablog"
                "&from=0"
                "&size=20"
            ),
        )


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
)
class WebsiteSearchInsightTest(WagtailTestUtils, TestCase):
    maxDiff = None
    test_url = reverse_lazy("search-website")

    def setUp(self):
        super().setUp()

        # create insight page object
        home = HomePage.objects.get()
        insights_index_page = InsightsIndexPage(
            title="Insight Pages", sub_heading="Sub heading"
        )
        home.add_child(instance=insights_index_page)
        insights_page = InsightsPage(
            title="William Shakespeare", sub_heading="Sub heading"
        )
        insights_index_page.add_child(instance=insights_page)

        # create insight page response in sourceUrl
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_insight.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json.loads(f.read()),
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
                "&filterAggregations=group%3Ainsight"
                "&from=0"
                "&size=20"
            ),
        )

    @responses.activate
    def test_template_used(self):
        response = self.get_url(self.test_url, group="insight")
        self.assertTemplateUsed(response, "search/catalogue_search.html")

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
            response.context_data["page"].object_list[0]["source_page"], InsightsPage
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

        # create insight page response in sourceUrl
        path = f"{settings.BASE_DIR}/etna/search/tests/fixtures/website_search_highlight.json"
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/search",
                json=json.loads(f.read()),
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
                "&filterAggregations=group%3Ahighlight"
                "&from=0"
                "&size=20"
            ),
        )

    @responses.activate
    def test_template_used(self):
        response = self.get_url(self.test_url, group="highlight")
        self.assertTemplateUsed(response, "search/catalogue_search.html")

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
