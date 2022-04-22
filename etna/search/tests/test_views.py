from unittest import mock

from django.http import HttpResponse
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

import responses

from ...ciim.tests.factories import create_response


class SearchViewTestCase(SimpleTestCase):
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

    def get(self, url: str, **data: Any):
        # Request the URL with render_to_response() patched to avoid
        # any database queries that are triggered during rendering
        with mock.patch(
            "etna.search.views.BaseSearchView.render_to_response",
            return_value=HttpResponse(""),
        ):
            return self.client.get(url, data=data)


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class CatalogueSearchAPIIntegrationTest(SearchViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("search-catalogue")

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.get(self.url)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=evidential"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=catalogueSource%3A10"
                "&aggregations=closure%3A10"
                "&aggregations=collection%3A10"
                "&aggregations=level%3A10"
                "&aggregations=topic%3A10"
                "&aggregations=group%3A30"
                "&aggregations=heldBy%3A10"
                "&filterAggregations=group%3Atna"
                "&from=0"
                "&size=20"
            ),
        )


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class CatalogueSearchLongFilterChooserAPIIntegrationTest(SearchViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            "search-catalogue-long-filter-chooser", kwargs={"field_name": "collection"}
        )

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.get(self.url)

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


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class FeaturedSearchAPIIntegrationTest(SearchViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("search-featured")

    @responses.activate
    def test_accessing_page_with_no_params_performs_search(self):
        self.get(self.url)

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
        self.get(self.url, q="query")

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


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class WebsiteSearchAPIIntegrationTest(SearchViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("search-website")

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.get(self.url)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=interpretive"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=catalogueSource%3A10"
                "&aggregations=closure%3A10"
                "&aggregations=collection%3A10"
                "&aggregations=level%3A10"
                "&aggregations=topic%3A10"
                "&aggregations=group%3A30"
                "&filterAggregations=group%3Ablog"
                "&from=0"
                "&size=20"
            ),
        )
