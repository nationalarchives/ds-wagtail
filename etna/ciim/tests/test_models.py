from django.test import SimpleTestCase

import responses

from ...records.api import get_records_client
from ...records.models import Record
from ..exceptions import DoesNotExist, KongAPIError, MultipleObjectsReturned
from .factories import create_record, create_search_response


class ManagerExceptionTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()

    @responses.activate
    def test_raises_does_not_exist(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json={"hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}},
        )

        with self.assertRaises(DoesNotExist):
            self.records_client.fetch(iaid="C140")

    @responses.activate
    def test_raises_multiple_objects_returned(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json={"hits": {"total": {"value": 2, "relation": "eq"}, "hits": [{}, {}]}},
        )

        with self.assertRaises(MultipleObjectsReturned):
            self.records_client.fetch(iaid="C140")


class SearchManagerFilterTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()

    @responses.activate
    def test_hits_returns_list(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_search_response(
                total_count=2,
                records=[
                    create_record(iaid="C4122893"),
                    create_record(iaid="C4122894"),
                ],
            ),
        )

        _, results = self.records_client.search(web_reference="ADM 223/3")

        self.assertEqual(results.total_count, 2)
        self.assertEqual(len(results), 2)
        self.assertTrue(isinstance(results[0], Record))
        self.assertTrue(isinstance(results[1], Record))
        self.assertEqual(results[0].iaid, "C4122893")
        self.assertEqual(results[1].iaid, "C4122894")

    @responses.activate
    def test_fetch_for_record_out_of_bounds_raises_index_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_search_response(records=[create_record()]),
        )

        _, results = self.records_client.search(web_reference="ADM 223/3")

        with self.assertRaises(IndexError):
            results.hits[1]


class KongExceptionTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()

    @responses.activate
    def test_raises_invalid_iaid_match(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            status=500,
        )

        with self.assertRaises(KongAPIError):
            self.records_client.fetch(iaid="C140")
