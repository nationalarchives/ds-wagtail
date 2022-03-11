from django.test import TestCase, override_settings

from wagtail.tests.utils import WagtailTestUtils

import responses

from ...ciim.tests.factories import create_response


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class CatalogueSearchIntegrationTest(WagtailTestUtils, TestCase):
    def setUp(self):
        super().setUp()

        self.login()

        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json={
                "responses": [
                    create_response(),
                    create_response(
                        aggregations={
                            "level": {"buckets": [{"key": "Item", "doc_count": 234}]},
                            "topic": {"buckets": [{"key": "Item", "doc_count": 234}]},
                            "collection": {
                                "buckets": [{"key": "Item", "doc_count": 234}]
                            },
                            "closure": {"buckets": [{"key": "Item", "doc_count": 234}]},
                            "catalogueSource": {
                                "buckets": [{"key": "Item", "doc_count": 234}]
                            },
                        }
                    ),
                ]
            },
        )

    @responses.activate
    def test_empty_search(self):
        self.client.get("/search/catalogue/")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/search"
                "?dateField=dateOpening"
                "&sort="
                "&sortOrder=asc"
                "&template=details"
                "&aggregations=catalogueSource%2C+closure%2C+collection%2C+group%2C+level%2C+topic"
                "&filterAggregations=group%3Atna"
                "&from=0"
                "&size=20"
            ),
        )
