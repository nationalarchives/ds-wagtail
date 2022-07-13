from django.test import SimpleTestCase, TestCase, override_settings

import responses

from ...records.models import Record
from ..exceptions import DoesNotExist, KongAPIError, MultipleObjectsReturned
from ..models import APIManager
from .factories import create_record, create_response


class DeprecatedSearchManagerTest(SimpleTestCase):
    @responses.activate
    def test_search_property_raises_deprecation_warning(self):
        with self.assertRaisesMessage(
            DeprecationWarning, "Record.search is deprecated. Use Record.api instead."
        ):
            Record.search.fetch(iaid="C140")


@override_settings(KONG_CLIENT_BASE_URL="https://kong.test")
class ManagerExceptionTest(TestCase):
    def setUp(self):
        self.manager = APIManager("records.Record")

    @responses.activate
    def test_raises_does_not_exist(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json={"hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}},
        )

        with self.assertRaises(DoesNotExist):
            self.manager.fetch(iaid="C140")

    @responses.activate
    def test_raises_multiple_objects_returned(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json={"hits": {"total": {"value": 2, "relation": "eq"}, "hits": [{}, {}]}},
        )

        with self.assertRaises(MultipleObjectsReturned):
            self.manager.fetch(iaid="C140")


@override_settings(KONG_CLIENT_BASE_URL="https://kong.test")
class SearchManagerFilterTest(TestCase):
    def setUp(self):
        self.manager = Record.api

    @responses.activate
    def test_hits_returns_list(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[create_record(iaid="C4122893"), create_record(iaid="C4122894")]
            ),
        )

        count, results = self.manager.search(web_reference="ADM 223/3")

        self.assertEqual(count, 2)
        self.assertEqual(len(results), 2)
        self.assertTrue(isinstance(results[0], Record))
        self.assertTrue(isinstance(results[1], Record))
        self.assertEqual(results[0].iaid, "C4122893")
        self.assertEqual(results[1].iaid, "C4122894")

    @responses.activate
    def test_fetch_for_record_out_of_bounds_raises_key_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(records=[create_record()]),
        )

        _, results = self.manager.search(web_reference="ADM 223/3")

        with self.assertRaises(IndexError):
            results[1]


class SearchManagerKongCount(TestCase):
    def setUp(self):
        self.manager = APIManager("records.Record")

        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(records=[create_record()]),
        )


class KongExceptionTest(TestCase):
    def setUp(self):
        self.manager = APIManager("records.Record")

    @responses.activate
    def test_raises_invalid_iaid_match(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            status=500,
        )

        with self.assertRaises(KongAPIError):
            self.manager.fetch(iaid="C140")
