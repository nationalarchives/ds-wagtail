from pathlib import Path

from django.test import TestCase, override_settings

import responses

from ..models import SearchManager
from ..exceptions import (
    DoesNotExist,
    MultipleObjectsReturned,
    InvalidCatalogueIdMatch,
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
            "https://kong.test/search",
            json={"hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}},
        )

        with self.assertRaises(DoesNotExist):
            self.manager.get(catalogue_id="C140")

    @responses.activate
    def test_raises_multiple_objects_returned(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json={"hits": {"total": {"value": 2, "relation": "eq"}, "hits": [{}, {}]}},
        )

        with self.assertRaises(MultipleObjectsReturned):
            self.manager.get(catalogue_id="C140")

    @responses.activate
    def test_raises_invalid_catalogue_id_match(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json={
                "hits": {
                    "total": {"value": 1, "relation": "eq"},
                    "hits": [
                        {"_source": {"@admin": {"id": "invalid"}}},
                    ],
                }
            },
        )

        with self.assertRaises(InvalidCatalogueIdMatch):
            self.manager.get(catalogue_id="C140")


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test", KONG_CLIENT_TEST_MODE=False
)
class KongExceptionTest(TestCase):
    def setUp(self):
        self.manager = SearchManager("records.RecordPage")

    @responses.activate
    def test_raises_invalid_catalogue_id_match(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            status=500,
        )

        with self.assertRaises(KongException):
            self.manager.get(catalogue_id="C140")


@override_settings(
    KONG_CLIENT_TEST_MODE=True,
    KONG_CLIENT_TEST_FILENAME=Path(Path(__file__).parent, "fixtures/record.json"),
)
class ModelTranslationTest(TestCase):
    @classmethod
    @responses.activate
    def setUpClass(cls):
        super().setUpClass()

        manager = SearchManager("records.RecordPage")

        cls.record_page = manager.get(catalogue_id="C140")

    def test_catalogue_id(self):
        self.assertEqual(self.record_page.catalogue_id, "C140")

    def test_title(self):
        self.assertEqual(
            self.record_page.title,
            "Records of the Natural Environment Research Council",
        )

    def test_reference_number(self):
        self.assertEqual(self.record_page.reference_number, "HA")

    def test_description(self):
        self.assertEqual(
            self.record_page.description, '<span class="head">description</span>'
        )

    def test_date_start(self):
        self.assertEqual(self.record_page.date_start, 1998)

    def test_date_end(self):
        self.assertEqual(self.record_page.date_end, 2013)

    def test_date_range(self):
        self.assertEqual(self.record_page.date_range, "1998-2013")

    def test_legal_status(self):
        self.assertEqual(self.record_page.legal_status, "Public Record(s)")
