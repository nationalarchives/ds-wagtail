import responses
from django.conf import settings
from django.test import SimpleTestCase, override_settings

from ...records.api import get_records_client
from ...records.models import Record
from ..exceptions import ClientAPIError, DoesNotExist, MultipleObjectsReturned
from .factories import create_record, create_search_response


@override_settings(CLIENT_BASE_URL=f"{settings.CLIENT_BASE_URL}")
class ClientAPIExceptionTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()

    @responses.activate
    def test_raises_does_not_exist(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json={
                "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}
            },
        )

        with self.assertRaises(DoesNotExist):
            self.records_client.fetch(iaid="C140")

    @responses.activate
    def test_raises_multiple_objects_returned(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json={
                "hits": {
                    "total": {"value": 2, "relation": "eq"},
                    "hits": [{}, {}],
                }
            },
        )

        with self.assertRaises(MultipleObjectsReturned):
            self.records_client.fetch(iaid="C140")


@override_settings(CLIENT_BASE_URL=f"{settings.CLIENT_BASE_URL}")
class ClientAPIFilterTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()

    @responses.activate
    def test_hits_returns_list(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json=create_search_response(
                total_count=2,
                records=[
                    create_record(iaid="C4122893"),
                    create_record(iaid="C4122894"),
                ],
            ),
        )

        result = self.records_client.search(web_reference="ADM 223/3")

        self.assertEqual(result.total_count, 2)
        self.assertEqual(len(result), 2)
        self.assertTrue(isinstance(result.hits[0], Record))
        self.assertTrue(isinstance(result.hits[1], Record))
        self.assertEqual(result.hits[0].iaid, "C4122893")
        self.assertEqual(result.hits[1].iaid, "C4122894")

    @responses.activate
    def test_fetch_for_record_out_of_bounds_raises_index_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json=create_search_response(records=[create_record()]),
        )

        result = self.records_client.search(web_reference="ADM 223/3")

        with self.assertRaises(IndexError):
            result.hits[1]


class ClientExceptionTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()

    @responses.activate
    def test_raises_invalid_iaid_match(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            status=500,
        )

        with self.assertRaises(ClientAPIError):
            self.records_client.fetch(iaid="C140")
