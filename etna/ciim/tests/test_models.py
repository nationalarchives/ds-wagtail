from pathlib import Path

from django.test import TestCase, override_settings

import responses

from ..models import SearchManager
from ..exceptions import (
    DoesNotExist,
    MultipleObjectsReturned,
    KongException,
)
from ...records.models import RecordPage


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test", KONG_CLIENT_TEST_MODE=False
)
class ManagerExceptionTest(TestCase):
    def setUp(self):
        self.manager = SearchManager("records.RecordPage")

    @responses.activate
    def test_raises_does_not_exist(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json={"hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}},
        )

        with self.assertRaises(DoesNotExist):
            self.manager.get(iaid="C140")

    @responses.activate
    def test_raises_multiple_objects_returned(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json={"hits": {"total": {"value": 2, "relation": "eq"}, "hits": [{}, {}]}},
        )

        with self.assertRaises(MultipleObjectsReturned):
            self.manager.get(iaid="C140")


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test", KONG_CLIENT_TEST_MODE=False
)
class SearchManagerFilterTest(TestCase):
    def setUp(self):
        self.manager = SearchManager("records.RecordPage")

    @responses.activate
    def test_no_hits_returns_empty_list(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json={"hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}},
        )

        results = self.manager.filter(iaid="C140")

        self.assertEqual(results, [])

    @responses.activate
    def test_hits_returns_list(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json={
                "hits": {
                    "total": {"value": 2, "relation": "eq"},
                    "hits": [
                        {
                            "_source": {
                                "@admin": {
                                    "id": "invalid",
                                },
                                "access": {"conditions": "open"},
                                "identifier": [
                                    {"iaid": "C4122893"},
                                    {"reference_number": "ADM 223/3"},
                                ],
                                "origination": {
                                    "creator": [{"name": [{"value": "test"}]}],
                                    "date": {
                                        "earliest": "1900",
                                        "latest": "2100",
                                        "value": "1900-2100",
                                    },
                                },
                                "description": [{"value": "description"}],
                                "legal": {"status": "Open"},
                            }
                        },
                        {
                            "_source": {
                                "@admin": {
                                    "id": "invalid",
                                },
                                "access": {"conditions": "open"},
                                "identifier": [
                                    {"iaid": "C4122894"},
                                    {"reference_number": "ADM 223/3"},
                                ],
                                "origination": {
                                    "creator": [{"name": [{"value": "test"}]}],
                                    "date": {
                                        "earliest": "1900",
                                        "latest": "2100",
                                        "value": "1900-2100",
                                    },
                                },
                                "description": [{"value": "description"}],
                                "legal": {"status": "Open"},
                            }
                        },
                    ],
                }
            },
        )

        results = self.manager.filter(reference_number="ADM 223/3")

        self.assertEqual(len(results), 2)
        self.assertTrue(isinstance(results[0], RecordPage))
        self.assertTrue(isinstance(results[1], RecordPage))
        self.assertEqual(results[0].iaid, "C4122893")
        self.assertEqual(results[1].iaid, "C4122894")


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test", KONG_CLIENT_TEST_MODE=False
)
class KongExceptionTest(TestCase):
    def setUp(self):
        self.manager = SearchManager("records.RecordPage")

    @responses.activate
    def test_raises_invalid_iaid_match(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            status=500,
        )

        with self.assertRaises(KongException):
            self.manager.get(iaid="C140")


@override_settings(
    KONG_CLIENT_TEST_MODE=True,
    KONG_CLIENT_TEST_FILENAME=Path(Path(__file__).parent, "fixtures/record.json"),
)
class SearchManagerTestModeTest(TestCase):
    def setUp(self):
        self.manager = SearchManager("records.RecordPage")

    def test_get_success(self):
        record_page = self.manager.get(iaid="C10297")

        self.assertTrue(isinstance(record_page, RecordPage))
        self.assertEquals(record_page.iaid, "C10297")

    def test_get_fail(self):
        with self.assertRaises(DoesNotExist):
            record_page = self.manager.get(iaid="fail")

    @override_settings(
        KONG_CLIENT_TEST_FILENAME=Path(
            Path(__file__).parent,
            "fixtures/multiple_records_with_matching_reference_numbers.json",
        ),
    )
    def test_filter_on_iaid_success(self):
        results = self.manager.filter(iaid="C30549")

        self.assertTrue(isinstance(results[0], RecordPage))
        self.assertEquals(results[0].iaid, "C30549")

    @override_settings(
        KONG_CLIENT_TEST_FILENAME=Path(
            Path(__file__).parent,
            "fixtures/multiple_records_with_matching_reference_numbers.json",
        ),
    )
    def test_filter_on_referecen_number_success(self):
        results = self.manager.filter(reference_number="ADM 223/3")

        self.assertTrue(isinstance(results[0], RecordPage))
        self.assertEquals(results[0].iaid, "C7171681")

    @override_settings(
        KONG_CLIENT_TEST_FILENAME=Path(
            Path(__file__).parent,
            "fixtures/multiple_records_with_matching_reference_numbers.json",
        ),
    )
    def test_filter_fail(self):
        results = self.manager.filter(iaid="fail")

        self.assertEquals(len(results), 0)


@override_settings(
    KONG_CLIENT_TEST_MODE=True,
    KONG_CLIENT_TEST_FILENAME=Path(Path(__file__).parent, "fixtures/record.json"),
)
class ModelTranslationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        manager = SearchManager("records.RecordPage")

        cls.record_page = manager.get(iaid="C10297")

    def test_instance(self):
        self.assertTrue(isinstance(self.record_page, RecordPage))

    def test_iaid(self):
        self.assertEqual(self.record_page.iaid, "C10297")

    def test_title(self):
        self.assertEqual(
            self.record_page.title,
            "Law Officers' Department: Registered Files",
        )

    def test_reference_number(self):
        self.assertEqual(self.record_page.reference_number, "LO 2")

    def test_description(self):
        self.assertEqual(
            self.record_page.description,
            '<span class="scopecontent"><span class="head">Scope and Content</span><span class="p">This series contains papers concering a wide variety of legal matters referred to the Law Officers for their advice or approval and includes applications for the Attorney General\'s General Fiat for leave to appeal to the House of Lords in criminal cases.</span><span class="p">Also included are a number of opinions, more of which can be found in <a href="/catalogue/C10298/">LO 3</a></span></span>',
        )

    def test_date_start(self):
        self.assertEqual(self.record_page.date_start, "1885-01-01")

    def test_date_end(self):
        self.assertEqual(self.record_page.date_end, "1979-12-31")

    def test_date_range(self):
        self.assertEqual(self.record_page.date_range, "1885-1979")

    def test_legal_status(self):
        self.assertEqual(self.record_page.legal_status, "Public Record(s)")
