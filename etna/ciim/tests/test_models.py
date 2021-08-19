from functools import partial
from pathlib import Path
import json

from django.test import TestCase, override_settings

import responses

from ..models import SearchManager
from ..exceptions import (
    DoesNotExist,
    MultipleObjectsReturned,
    KongException,
    UnsupportedSlice,
)
from ...records.models import RecordPage
from .factories import create_record, create_response, paginate_records_callback


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
        self.manager = RecordPage.search

    @responses.activate
    def test_hits_returns_list(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(
                records=[create_record(iaid="C4122893"), create_record(iaid="C4122894")]
            ),
        )

        results = self.manager.filter(reference_number="ADM 223/3")

        self.assertEqual(len(results), 2)
        self.assertTrue(isinstance(results[0], RecordPage))
        self.assertTrue(isinstance(results[1], RecordPage))
        self.assertEqual(results[0].iaid, "C4122893")
        self.assertEqual(results[1].iaid, "C4122894")

    @responses.activate
    def test_fetch_for_record_out_of_bounds_raises_key_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(records=[create_record()]),
        )

        results = self.manager.filter(reference_number="ADM 223/3")

        with self.assertRaises(IndexError):
            results[1]

    @responses.activate
    def test_comprehension_returns_model_instances(self):

        records = [
            create_record(iaid="C4122893", reference_number="ADM 223/3"),
            create_record(iaid="C4122894", reference_number="ADM 223/3"),
        ]

        responses.reset()
        responses.add_callback(
            responses.GET,
            "https://kong.test/search",
            callback=partial(paginate_records_callback, records),
        )

        results = [r for r in self.manager.filter(reference_number="ADM 223/3")]

        self.assertEqual(len(results), 2)
        self.assertTrue(isinstance(results[0], RecordPage))
        self.assertTrue(isinstance(results[1], RecordPage))
        self.assertEqual(results[0].iaid, "C4122893")
        self.assertEqual(results[1].iaid, "C4122894")


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test", KONG_CLIENT_TEST_MODE=False
)
class SearchManagerKongCount(TestCase):
    def setUp(self):
        self.manager = SearchManager("records.RecordPage")

        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(records=[create_record()]),
        )

    @responses.activate
    def test_hits_with_subscript_for_first_result(self):
        result = self.manager.filter(reference_number="ADM 223/3")

        self.assertEqual(len(result), 1)
        self.assertEqual(result.count(), 1)


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test", KONG_CLIENT_TEST_MODE=False
)
class SearchManagerKongClientIntegrationTest(TestCase):
    def setUp(self):
        self.manager = RecordPage.search

        records = [create_record() for r in range(0, 15)]

        responses.reset()
        responses.add_callback(
            responses.GET,
            "https://kong.test/search",
            callback=partial(paginate_records_callback, records),
        )

    @responses.activate
    def test_url_for_with_subscript_for_first_result(self):

        result = self.manager.filter(reference_number="ADM 223/3")[0]

        self.assertEqual(len(responses.calls), 1)
        self.assertURLEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?term=ADM+223%2F3&from=0&size=10&pretty=false",
        )

    @responses.activate
    def test_url_for_subscript_for_first_result_with_limit(self):
        result = self.manager.filter(reference_number="ADM 223/3")[0:1]

        self.assertEqual(len(responses.calls), 1)
        self.assertURLEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?term=ADM+223%2F3&from=0&size=1&pretty=false",
        )

    @responses.activate
    def test_url_for_subscript_for_second_result_with_limit(self):
        result = self.manager.filter(reference_number="ADM 223/3")[0:1]

        self.assertEqual(len(responses.calls), 1)
        self.assertURLEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?term=ADM+223%2F3&from=0&size=1&pretty=false",
        )

    @responses.activate
    def test_url_for_subscript_for_first_page(self):
        result = self.manager.filter(reference_number="ADM 223/3")[0:5]

        results = result[0]

        self.assertEqual(len(responses.calls), 1)
        self.assertURLEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?term=ADM+223%2F3&from=0&size=5&pretty=false",
        )

    @responses.activate
    def test_url_for_subscript_for_second_page(self):
        result = self.manager.filter(reference_number="ADM 223/3")[5:10]

        self.assertEqual(len(responses.calls), 1)
        self.assertURLEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?term=ADM+223%2F3&from=5&size=5&pretty=false",
        )

    @responses.activate
    def test_url_for_subscript_for_third_page(self):
        result = self.manager.filter(reference_number="ADM 223/3")[10:15]

        self.assertEqual(len(responses.calls), 1)
        self.assertURLEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?term=ADM+223%2F3&from=10&size=5&pretty=false",
        )

    @responses.activate
    def test_slicing_with_step_raises_slice_error(self):
        with self.assertRaisesMessage(
            UnsupportedSlice, "Slicing with step is not supported"
        ):
            result = self.manager.filter(reference_number="ADM 223/3")[0:1:1]

    @responses.activate
    def test_slicing_with_negative_index_raises_slice_error(self):
        with self.assertRaisesMessage(
            UnsupportedSlice, "Slicing with negative index not supported"
        ):
            self.manager.filter(reference_number="ADM 223/3")[-1]

            self.assertEqual(len(responses.calls), 0)

    @responses.activate
    def test_slicing_for_all_raises_slice_error(self):
        with self.assertRaisesMessage(
            UnsupportedSlice, "Slicing to return all records ([:]) is not supported"
        ):
            result = self.manager.filter(reference_number="ADM 223/3")[:]

    @responses.activate
    def test_len_performs_fetch_for_zero_results(self):
        result = self.manager.filter(reference_number="ADM 223/3")
        count = result.count()

        self.assertEqual(len(responses.calls), 1)
        self.assertURLEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?term=ADM+223%2F3&from=0&size=0&pretty=false",
        )

    @responses.activate
    def test_count_performs_fetch_for_zero_results(self):
        result = self.manager.filter(reference_number="ADM 223/3")
        count = len(result)

        self.assertEqual(len(responses.calls), 1)
        self.assertURLEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?term=ADM+223%2F3&from=0&size=0&pretty=false",
        )

    @responses.activate
    def test_iteration_performs_fetch(self):
        for result in self.manager.filter(reference_number="ADM 223/3"):
            ...

        self.assertTrue(len(responses.calls) > 0)

    @responses.activate
    def test_comprehension_performs_fetch(self):
        result = [r for r in self.manager.filter(reference_number="ADM 223/3")]

        self.assertTrue(len(responses.calls) > 0)

    @responses.activate
    def test_cast_to_list_performs_fetch(self):
        result = list(self.manager.filter(reference_number="ADM 223/3"))

        self.assertTrue(len(responses.calls) > 0)

    @responses.activate
    def test_iterator(self):

        pages = self.manager.filter(reference_number="ADM 223/3")

        self.assertEquals(len(pages), 15)
        self.assertEquals(len([p for p in pages]), 15)


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
        self.manager = RecordPage.search

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
        KONG_CLIENT_TEST_FILENAME=Path(
            Path(__file__).parent,
            "fixtures/multiple_records_with_matching_reference_numbers.json",
        ),
    )
    def test_filter_on_multiple_iaids(self):
        results = self.manager.get_multiple(iaid=["C30549", "C7171681"])

        self.assertEquals(len(results), 2)
        self.assertEquals(results[0].iaid, "C30549")
        self.assertEquals(results[1].iaid, "C7171681")

    @override_settings(
        KONG_CLIENT_TEST_FILENAME=Path(
            Path(__file__).parent,
            "fixtures/multiple_records_with_matching_reference_numbers.json",
        ),
    )
    def test_failed_fetch_skips_record(self):
        results = self.manager.get_multiple(iaid=["C30549", "invalid", "C7171681"])

        self.assertEquals(len(results), 2)
        self.assertEquals(results[0].iaid, "C30549")
        self.assertEquals(results[1].iaid, "C7171681")


@override_settings(
    KONG_CLIENT_TEST_MODE=True,
    KONG_CLIENT_TEST_FILENAME=Path(Path(__file__).parent, "fixtures/record.json"),
)
class ModelTranslationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        manager = RecordPage.search

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

    def test_origination_date(self):
        self.assertEqual(self.record_page.origination_date, "1885-1979")

    def test_legal_status(self):
        self.assertEqual(self.record_page.legal_status, "Public Record(s)")

    def test_held_by(self):
        self.assertEqual(self.record_page.held_by, "The National Archives, Kew")

    def test_is_digitised(self):
        self.assertEqual(self.record_page.is_digitised, True)

    def test_parent(self):
        self.assertEqual(
            self.record_page.parent,
            {
                "iaid": "C199",
                "reference_number": "HO 42",
                "title": "Records created or inherited by the Law Officers' Department",
            },
        )

    def test_hierarchy(self):
        self.assertEqual(
            self.record_page.hierarchy,
            [
                {
                    "reference_number": "FCO 13",
                    "title": "Foreign and Commonwealth Office and predecessors: Cultural Relations Departments:...",
                },
                {
                    "reference_number": "FCO 13/775",
                    "title": "Centrepiece for celebrations of bicentenary of USA in 1976: loan of Magna Carta from...",
                },
            ],
        )

    def test_is_digitised(self):
        self.assertEqual(self.record_page.is_digitised, True)

    def test_availablility_access_display_label(self):
        self.assertEqual(
            self.record_page.availablility_access_display_label,
            'NO "Access conditions" STATED',
        )

    def test_availablility_access_closure_label(self):
        self.assertEqual(
            self.record_page.availablility_access_closure_label,
            "Open Document, Open Description",
        )

    def test_availablility_delivery_condition(self):
        self.assertEqual(
            self.record_page.availablility_delivery_condition, "DigitizedDiscovery"
        )

    def test_availablility_delivery_surrogates(self):
        self.assertEqual(
            self.record_page.availablility_delivery_surrogates,
            [
                {
                    "type": "surrogate",
                    "value": '<a target="_blank" href="http://www.thegenealogist.co.uk/non-conformist-records">The Genealogist</a>',
                },
                {
                    "type": "surrogate",
                    "value": '<a target="_blank" href="http://search.ancestry.co.uk/search/db.aspx?dbid=5111">Ancestry</a>',
                },
            ],
        )

    def test_topics(self):
        self.assertEqual(
            self.record_page.topics,
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
            self.record_page.next_record,
            {
                "iaid": "C441750",
            },
        )

    def test_previous_record(self):
        self.assertEqual(
            self.record_page.previous_record,
            {
                "iaid": "C441748",
            },
        )


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test", KONG_CLIENT_TEST_MODE=False
)
class UnexpectedParsingIssueTest(TestCase):
    """A collection of tests verifying fixes for real-world (but unexpected)
    issues with data returned by Kong"""

    @responses.activate
    def test_hierarchy_with_no_identifier_is_skipped(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="C123456",
                        hierarchy=[
                            {
                                "@summary": {
                                    "title": "Foreign and Commonwealth Office and predecessors: Cultural Relations Departments:..."
                                },
                            },
                        ],
                    ),
                ]
            ),
        )

        record_page = RecordPage.search.get(iaid="C123456")

        self.assertEqual(record_page.hierarchy, [])

    @responses.activate
    def test_record_with_origination_but_no_date(self):
        record = create_record(
            iaid="C123456",
        )
        del record['_source']['@origination']['date']

        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(records=[record]),
        )

        record_page = RecordPage.search.get(iaid="C123456")

        self.assertEqual(record_page.origination_date, None)
