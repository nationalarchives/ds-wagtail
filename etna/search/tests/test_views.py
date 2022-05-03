from django.test import TestCase, override_settings

from wagtail.tests.utils import WagtailTestUtils

import responses

from ...ciim.tests.factories import create_response


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class CatalogueSearchAPIIntegrationTest(WagtailTestUtils, TestCase):
    def setUp(self):
        super().setUp()

        self.login()

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

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get("/search/catalogue/")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=evidential"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=catalogueSource"
                "&aggregations=closure"
                "&aggregations=collection"
                "&aggregations=level"
                "&aggregations=topic"
                "&aggregations=group%3A30"
                "&aggregations=heldBy"
                "&filterAggregations=group%3Atna"
                "&from=0"
                "&size=20"
            ),
        )


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class CatalogueSearchLongFilterChooserAPIIntegrationTest(WagtailTestUtils, TestCase):
    def setUp(self):
        super().setUp()

        self.login()

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

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get("/search/catalogue/long-filter-chooser/collection/")

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
            ),
        )


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class FeaturedSearchAPIIntegrationTest(WagtailTestUtils, TestCase):
    def setUp(self):
        super().setUp()

        self.login()

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

    @responses.activate
    def test_accessing_page_with_no_params_performs_search(self):
        self.client.get("/search/featured/")

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
        self.client.get("/search/featured/?q=query")

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
class WebsiteSearchAPIIntegrationTest(WagtailTestUtils, TestCase):
    def setUp(self):
        super().setUp()

        self.login()

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

    @responses.activate
    def test_accessing_page_with_no_params_performs_empty_search(self):
        self.client.get("/search/website/")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?stream=interpretive"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=catalogueSource"
                "&aggregations=closure"
                "&aggregations=collection"
                "&aggregations=level"
                "&aggregations=topic"
                "&aggregations=group%3A30"
                "&filterAggregations=group%3Ablog"
                "&from=0"
                "&size=20"
            ),
        )
