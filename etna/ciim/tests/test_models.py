import json
import unittest

from pathlib import Path

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


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
)
class SearchManagerKongCount(TestCase):
    def setUp(self):
        self.manager = APIManager("records.Record")

        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(records=[create_record()]),
        )


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
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


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
)
class ModelTranslationTest(TestCase):
    @responses.activate
    def setUp(self):

        path = Path(Path(__file__).parent, "fixtures/record.json")
        with open(path, "r") as f:
            responses.add(
                responses.GET,
                "https://kong.test/data/fetch",
                json=json.loads(f.read()),
            )

        manager = Record.api

        self.record: Record = manager.fetch(iaid="C10297")

    def test_instance(self):
        self.assertTrue(isinstance(self.record, Record))

    def test_iaid(self):
        self.assertEqual(self.record.iaid, "C10297")

    def test_title(self):
        self.assertEqual(
            self.record.title,
            "Law Officers' Department: Registered Files",
        )

    def test_reference_number(self):
        self.assertEqual(self.record.reference_number, "LO 2")

    def test_description(self):
        self.assertEqual(
            self.record.description,
            (
                """<span class="scopecontent"><p>This series contains papers concering a wide variety of legal matters referred to the Law Officers for their advice or approval and includes applications for the Attorney General's General Fiat for leave to appeal to the House of Lords in criminal cases.</p><p>Also included are a number of opinions, more of which can be found in <a href="C10298">LO 3</a></p></span>"""
            ),
        )

    def test_origination_date(self):
        self.assertEqual(self.record.origination_date, "1885-1979")

    def test_legal_status(self):
        self.assertEqual(self.record.legal_status, "Public Record(s)")

    def test_held_by(self):
        self.assertEqual(self.record.held_by, "The National Archives, Kew")

    def test_parent(self):
        self.assertEqual(
            self.record.parent,
            {
                "iaid": "C199",
                "reference_number": "LO",
                "title": "Records created or inherited by the Law Officers' Department",
            },
        )

    def test_hierarchy(self):
        self.assertEqual(
            self.record.hierarchy,
            [
                {
                    "reference_number": "LO",
                    "title": "Records created or inherited by the Law Officers' Department",
                },
                {
                    "reference_number": "LO 2",
                    "title": "Law Officers' Department: Registered Files",
                },
                {
                    "reference_number": "ADM 171",
                    "title": "Admiralty, and Ministry of Defence, Navy Department: Medal Rolls",
                },
            ],
        )

    @unittest.skip("Data not supported for the json record")
    def test_is_digitised(self):
        self.assertEqual(self.record.is_digitised, True)

    @unittest.skip("Data not supported for the json record")
    def test_availability_delivery_condition(self):
        self.assertEqual(
            self.record.availability_delivery_condition, "DigitizedDiscovery"
        )

    @unittest.skip("Data not supported for the json record")
    def test_availability_delivery_surrogates(self):
        self.assertEqual(
            self.record.availability_delivery_surrogates,
            [
                {
                    "type": "surrogate",
                    "value": (
                        '<a target="_blank" href="http://www.thegenealogist.co.uk/non-conformist-records">'
                        "The Genealogist"
                        "</a>"
                    ),
                },
                {
                    "type": "surrogate",
                    "value": (
                        '<a target="_blank" href="http://search.ancestry.co.uk/search/db.aspx?dbid=5111">'
                        "Ancestry"
                        "</a>"
                    ),
                },
            ],
        )

    @unittest.skip("Data not supported for the json record")
    def test_topics(self):
        self.assertEqual(
            self.record.topics,
            [
                {
                    "title": "Taxonomy One",
                },
                {
                    "title": "Taxonomy Two",
                },
                {
                    "title": "Taxonomy Three",
                },
            ],
        )

    def test_next_record(self):
        self.assertEqual(
            self.record.next_record,
            {
                "iaid": "C10298",
            },
        )

    def test_previous_record(self):
        self.assertEqual(
            self.record.previous_record,
            {
                "iaid": "C10296",
            },
        )

    @unittest.skip("Data not supported for the json record")
    def test_related_records(self):
        self.assertEqual(
            self.record.related_records,
            [
                {
                    "iaid": "C8981250",
                    "title": "[1580-1688]. Notes (cards) from State Papers Foreign, Royal "
                    "Letters, SP 102/61. Manuscript.",
                }
            ],
        )

    @unittest.skip("Data not supported for the json record")
    def test_related_articles(self):
        self.assertEqual(
            self.record.related_articles,
            [
                {
                    "title": "Irish maps c.1558-c.1610",
                    "url": (
                        "http://www.nationalarchives.gov.uk/help-with-your-research/research-guides/"
                        "irish-maps-c1558-c1610/"
                    ),
                }
            ],
        )

    def test_catalogue_source(self):
        self.assertEqual(self.record.catalogue_source, "CAT")

    def test_repo_summary_title(self):
        self.assertEqual(self.record.repo_summary_title, "The National Archives")

    def test_repo_archon_value(self):
        self.assertEqual(self.record.repo_archon_value, "66")

    def test_level_code(self):
        self.assertEqual(self.record.level_code, "3")

    def test_level(self):
        self.assertEqual(self.record.level, "Series")

    def test_template_summary_title(self):
        self.assertEqual(
            self.record.template_summary_title,
            "Law Officers' Department: Registered Files",
        )

    def test_data_source(self):
        self.assertEqual(self.record.data_source, "mongo")

    def test_related_materials(self):
        self.assertEqual(
            self.record.related_materials,
            [
                {
                    "description": "For files of the tri-service Defence Intelligence staff see,",
                    "links": [{"iaid": "C5789", "text": "DEFE 31"}],
                },
                {
                    "description": "For records of the Joint Intelligence Bureau see",
                    "links": [{"iaid": "C14457", "text": "WO 252"}],
                },
                {
                    "description": "Records of the Government Code and Cypher School:",
                    "links": [],
                },
            ],
        )


@override_settings(KONG_CLIENT_BASE_URL="https://kong.test")
class UnexpectedParsingIssueTest(TestCase):
    """A collection of tests verifying fixes for real-world (but unexpected)
    issues with data returned by Kong"""

    @responses.activate
    def test_hierarchy_with_no_identifier_is_skipped(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="C123456",
                        hierarchy=[
                            {
                                "@summary": {
                                    "title": (
                                        "Foreign and Commonwealth Office and predecessors: "
                                        "Cultural Relations Departments:..."
                                    )
                                },
                            },
                        ],
                    ),
                ]
            ),
        )

        record = Record.api.fetch(iaid="C123456")

        self.assertEqual(record.hierarchy, [])

    @responses.activate
    def test_record_with_origination_but_no_date(self):
        record = create_record(
            iaid="C123456",
        )
        del record["_source"]["origination"]["date"]

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(records=[record]),
        )

        record = Record.api.fetch(iaid="C123456")

        self.assertEqual(record.origination_date, "")

    @responses.activate
    def test_related_record_with_no_identifier(self):
        record = create_record(
            related=[
                {
                    "@admin": {
                        "id": "C568",
                        "uuid": "216d37d3-eb15-3e76-99d2-bc9ee99104ce",
                    },
                    "@entity": "reference",
                    "@link": {
                        "note": {
                            "value": "For records originating in the Exchequer see"
                        },
                        "qualifier": "association",
                        "relationship": {"value": "related"},
                    },
                    "summary": {
                        "title": "Records of the Office of First Fruits and Tenths"
                    },
                }
            ],
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(records=[record]),
        )

        record = Record.api.fetch(iaid="C123456")

        # Related records with no 'Aidentifer' and therefore no
        # reference_nubmers were skipped but now we're linking to the details
        # page using the iaid, these records should be present
        self.assertEqual(
            record.related_records,
            [
                {
                    "iaid": "C568",
                    "title": "Records of the Office of First Fruits and Tenths",
                }
            ],
        )

    @responses.activate
    def test_related_article_with_no_title(self):
        record = create_record(
            iaid="C123456",
            related=[
                {
                    "@admin": {
                        "id": "rg-1582",
                        "source": "wagtail-es",
                        "uuid": "890bc89e-9c9d-37a8-bdd4-1213bad92a33",
                    },
                    "@entity": "reference",
                    "@type": {"base": "media", "type": "research guide"},
                    "source": {
                        "location": (
                            "http://www.nationalarchives.gov.uk/"
                            "help-with-your-research/research-guides/famous-wills-1552-1854/"
                        )
                    },
                }
            ],
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(records=[record]),
        )

        record = Record.api.fetch(iaid="C123456")

        self.assertEqual(record.related_articles, [])
