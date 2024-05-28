import unittest

from datetime import date, datetime
from urllib.parse import quote

from django.conf import settings
from django.test import SimpleTestCase

import responses

from etna.ciim.constants import Aggregation, BucketKeys
from etna.ciim.tests.factories import (
    create_record,
    create_response,
    create_search_response,
)
from etna.core.utils import dotdict
from etna.records.api import get_records_client
from etna.records.models import Record

from ..client import ResultList, Sort, Stream
from ..exceptions import (
    ClientAPIBadRequestError,
    ClientAPICommunicationError,
    ClientAPIInternalServerError,
    ClientAPIServiceUnavailableError,
    DoesNotExist,
    MultipleObjectsReturned,
)


class ClientSearchTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json=create_search_response(),
        )

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.records_client.search()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url, f"{settings.CLIENT_BASE_URL}/search"
        )

    @responses.activate
    def test_with_q(self):
        self.records_client.search(q="Egypt")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?q=Egypt",
        )

    @unittest.skip("TODO: Keep, not in scope for Ohos-Etna at this time")
    @responses.activate
    def test_with_opening_start_date(self):
        self.records_client.search(
            opening_start_date=datetime(year=1901, month=2, day=3)
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?openingStartDate=1901-02-03T00%3A00%3A00",
        )

    @unittest.skip("TODO: Keep, not in scope for Ohos-Etna at this time")
    @responses.activate
    def test_with_opening_end_date(self):
        self.records_client.search(opening_end_date=datetime(year=1901, month=2, day=3))

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?openingEndDate=1901-02-03T00%3A00%3A00",
        )

    @responses.activate
    def test_with_covering_date_from(self):
        self.records_client.search(
            group=BucketKeys.COMMUNITY,
            covering_date_from=date(year=1901, month=2, day=3),
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?filter={quote('fromDate:(>=1901-02-03)')}",
        )

    @responses.activate
    def test_with_covering_date_to(self):
        self.records_client.search(
            group=BucketKeys.COMMUNITY, covering_date_to=date(year=1901, month=2, day=3)
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?filter={quote('toDate:(<=1901-02-03)')}",
        )

    @responses.activate
    def test_with_sort_title(self):
        for index, test_data in enumerate(
            (
                {
                    "label": "title ascending",
                    "value": Sort.TITLE_ASC,
                    "expected": f"{settings.CLIENT_BASE_URL}/search?sort={quote('title:asc')}",
                },
                {
                    "label": "title descending",
                    "value": Sort.TITLE_DESC,
                    "expected": f"{settings.CLIENT_BASE_URL}/search?sort={quote('title:desc')}",
                },
            )
        ):
            test_data = dotdict(test_data)
            with self.subTest(test_data.label):
                self.records_client.search(sort=test_data.value)
                self.assertEqual(
                    responses.calls[index].request.url,
                    test_data.expected,
                    test_data.label,
                )

    @responses.activate
    def test_with_sort_date(self):
        for index, test_data in enumerate(
            (
                {
                    "label": "date ascending",
                    "value": Sort.DATE_ASC,
                    "expected": f"{settings.CLIENT_BASE_URL}/search?sort={quote('date:asc')}",
                },
                {
                    "label": "date descending",
                    "value": Sort.DATE_DESC,
                    "expected": f"{settings.CLIENT_BASE_URL}/search?sort={quote('date:desc')}",
                },
            )
        ):
            test_data = dotdict(test_data)
            with self.subTest(test_data.label):
                self.records_client.search(sort=test_data.value)
                self.assertEqual(
                    responses.calls[index].request.url,
                    test_data.expected,
                    test_data.label,
                )

    @unittest.skip("TODO: Keep, not in scope for Ohos-Etna at this time")
    @responses.activate
    def test_with_sort_date_opening(self):
        self.records_client.search(sort=Sort.DATE_OPENING)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?sort=dateOpening",
        )

    @responses.activate
    def test_with_sort_relevance(self):
        self.records_client.search(sort=Sort.RELEVANCE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?sort=",
        )

    @responses.activate
    def test_with_aggregations(self):
        self.records_client.search(
            aggregations=[Aggregation.GROUP, Aggregation.COLLECTION]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?" "aggs=group" "&aggs=collection",
        )

    @responses.activate
    def test_with_filter_aggregations(self):
        self.records_client.search(
            filter_aggregations=[
                "group:community",
                "collection:SWOP",
            ]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?"
            "filter=group%3Acommunity"
            "&filter=collection%3ASWOP",
        )

    @responses.activate
    def test_with_filter_collection_special_values(self):
        self.records_client.search(filter_aggregations=["collection:value(1)"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?" "filter=collection%3Avalue%281%29",
        )

    @responses.activate
    def test_with_filter_collection_multiple_values(self):
        self.records_client.search(
            filter_aggregations=["collection:value1", "collection:value2"]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?"
            "filter=collection%3Avalue1"
            "&filter=collection%3Avalue2",
        )

    @responses.activate
    def test_with_filter_held_by_without_special_chars(self):
        self.records_client.search(filter_aggregations=["heldBy:Tate Gallery Archive"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?filter=heldBy%3ATate+Gallery+Archive",
        )

    @responses.activate
    def test_with_filter_held_by_with_special_chars(self):
        self.records_client.search(
            filter_aggregations=["heldBy:1/ 2( 3) 4: 5, 6& 7- 8| 9+ 10@ 11! 12."]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?filter=heldBy%3A1+2+3+4+5+6+7+8+9+10+11+12+",
        )

    @responses.activate
    def test_with_filter_held_by_with_special_chars_examples(self):
        self.maxDiff = None
        self.records_client.search(
            filter_aggregations=[
                "heldBy:Rolls-Royce plc",
                "heldBy:IRIE! dance theatre",
                "heldBy:Royal Yorkshire Lodge No. 265",
                "heldBy:REWIND| Artists' Video in the 70s & 80s",
                "heldBy:National Arts Education Archive @ YSP",
                "heldBy:Foster + Partners",
                "heldBy:Labour History Archive and Study Centre (People's History Museum/University of Central Lancashire)",
                "heldBy:London University: London School of Economics, The Women's Library",
            ]
        )
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?"
            "filter=heldBy%3ARolls+Royce+plc%3Aor"
            "&filter=heldBy%3AIRIE+dance+theatre%3Aor"
            "&filter=heldBy%3ARoyal+Yorkshire+Lodge+No+265%3Aor"
            "&filter=heldBy%3AREWIND+Artists%27+Video+in+the+70s+80s%3Aor"
            "&filter=heldBy%3ANational+Arts+Education+Archive+YSP%3Aor"
            "&filter=heldBy%3AFoster+Partners%3Aor"
            "&filter=heldBy%3ALabour+History+Archive+and+Study+Centre+People%27s+History+Museum+University+of+Central+Lancashire+%3Aor"
            "&filter=heldBy%3ALondon+University+London+School+of+Economics+The+Women%27s+Library%3Aor",
        )

    @responses.activate
    def test_with_filter_held_by_with_special_chars_not_prepared(self):
        self.records_client.search(filter_aggregations=["heldBy:People's"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?filter=heldBy%3APeople%27s",
        )

    @responses.activate
    def test_with_filter_level(self):
        self.records_client.search(filter_aggregations=["level:Item", "level:Piece"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?"
            "filter=level%3AItem%3Aor"
            "&filter=level%3APiece%3Aor",
        )

    @responses.activate
    def test_with_filter_type(self):
        self.records_client.search(
            filter_aggregations=["type:person", "type:organisation"]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?"
            "filter=type%3Aperson&"
            "filter=type%3Aorganisation",
        )

    @unittest.skip("TODO: Keep, not in scope for Ohos-Etna at this time")
    @responses.activate
    def test_with_filter_keyword(self):
        self.records_client.search(filter_keyword="filter keyword")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?filter=filter+keyword",
        )

    @responses.activate
    def test_with_offset(self):
        self.records_client.search(offset=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?from=20",
        )

    @responses.activate
    def test_with_size(self):
        self.records_client.search(size=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?size=20",
        )


@unittest.skip("TODO: Keep, not in scope for Ohos-Etna at this time")
class ClientSearchUnifiedTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()
        responses.add(
            responses.GET, f"{settings.CLIENT_BASE_URL}/searchUnified", json={}
        )

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.records_client.search_unified()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified",
        )

    @responses.activate
    def test_with_q(self):
        self.records_client.search_unified(q="Egypt")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?q=Egypt",
        )

    @responses.activate
    def test_with_web_reference(self):
        self.records_client.search_unified(web_reference="ADM/223/3")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?webReference=ADM%2F223%2F3",
        )

    @responses.activate
    def test_with_evidential_stream(self):
        self.records_client.search_unified(stream=Stream.EVIDENTIAL)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?stream=evidential",
        )

    @responses.activate
    def test_with_interpretive_stream(self):
        self.records_client.search_unified(stream=Stream.INTERPRETIVE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?stream=interpretive",
        )

    @responses.activate
    def test_with_sort_title(self):
        self.records_client.search_unified(sort_by=Sort.TITLE_ASC)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sort=title:asc",
        )

    @responses.activate
    def test_with_sort_date_created(self):
        self.records_client.search_unified(sort_by=Sort.DATE_ASC)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sort=dateCreated",
        )

    @responses.activate
    def test_with_sort_date_opening(self):
        self.records_client.search_unified(sort_by=Sort.DATE_OPENING)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sort=dateOpening",
        )

    @responses.activate
    def test_with_sort_relevance(self):
        self.records_client.search_unified(sort_by=Sort.RELEVANCE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sort=",
        )

    @responses.activate
    def test_with_sort_order_asc(self):
        self.records_client.search_unified(sort_order="")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sortOrder=asc",
        )

    @responses.activate
    def test_with_sort_order_desc(self):
        self.records_client.search_unified(sort_order="")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sortOrder=desc",
        )

    @responses.activate
    def test_with_offset(self):
        self.records_client.search_unified(offset=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?from=20",
        )

    @responses.activate
    def test_with_size(self):
        self.records_client.search_unified(size=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?size=20",
        )


class ClientFetchTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(status_code=400),
        )
        with self.assertRaises(DoesNotExist):
            self.records_client.get()

    @responses.activate
    def test_with_iaid(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(record=create_record(iaid="C198022")),
        )
        self.records_client.get(id="C198022")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/get?id=C198022",
        )

    @responses.activate
    def test_with_ciim_id(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(record=create_record(group="community")),
        )
        self.records_client.get(id="swop-0000000")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/get?id=swop-0000000",
        )


@unittest.skip("TODO: Keep, not in scope for Ohos-Etna at this time")
class ClientFetchAllTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()
        responses.add(responses.GET, f"{settings.CLIENT_BASE_URL}/fetchAll", json={})

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.records_client.fetch_all()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url, f"{settings.CLIENT_BASE_URL}/fetchAll"
        )

    @responses.activate
    def test_with_ids(self):
        self.records_client.fetch_all(ids=["id-one", "id-two", "id-three"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetchAll?ids=id-one&ids=id-two&ids=id-three",
        )

    @responses.activate
    def test_with_iaids(self):
        self.records_client.fetch_all(iaids=["iaid-one", "iaid-two", "iaid-three"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetchAll?metadataIds=iaid-one&metadataIds=iaid-two&metadataIds=iaid-three",
        )

    @responses.activate
    def test_with_rid(self):
        self.records_client.fetch_all(rid="rid-123")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetchAll?rid=rid-123",
        )

    @responses.activate
    def test_with_size(self):
        self.records_client.fetch_all(size=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetchAll?size=20",
        )


class TestClientFetchReponse(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()

    @responses.activate
    def test_raises_client_api_error_with_message(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json={"message": "failure to get a peer from the ring-balancer"},
            status=503,
        )

        with self.assertRaisesMessage(
            ClientAPIServiceUnavailableError,
            "failure to get a peer from the ring-balancer",
        ):
            self.records_client.get()

    @responses.activate
    def test_raises_client_api_error_on_elastic_search_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json={
                "error": {
                    "root_cause": [],
                    "type": "search_phase_execution_exception",
                    "reason": "all shards failed",
                    "phase": "query",
                    "grouped": True,
                    "failed_shards": [],
                },
                "status": 503,
            },
            status=503,
        )

        with self.assertRaisesMessage(
            ClientAPIServiceUnavailableError, "all shards failed"
        ):
            self.records_client.get()

    @responses.activate
    def test_raises_client_api_error_on_java_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json={
                "timestamp": "2021-08-26T09:07:31.688+00:00",
                "status": 400,
                "error": "Bad Request",
                "message": (
                    "Failed to convert value of type 'java.lang.String' "
                    "to required type 'java.lang.Integer'; "
                    "nested exception is java.lang.NumberFormatException: "
                    'For input string: "999999999999999999"'
                ),
                "path": "/get",
            },
            status=400,
        )

        with self.assertRaisesMessage(
            ClientAPIBadRequestError, "Failed to convert value of type"
        ):
            self.records_client.get()

    @responses.activate
    def test_internal_server_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json={
                "message": ("Internal Server Error"),
            },
            status=500,
        )

        with self.assertRaisesMessage(
            ClientAPIInternalServerError, "Internal Server Error"
        ):
            self.records_client.get()

    @responses.activate
    def test_default_exception(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json={
                "message": ("I'm a teapot"),
            },
            status=418,
        )

        with self.assertRaisesMessage(ClientAPICommunicationError, "I'm a teapot"):
            self.records_client.get()

    @responses.activate
    def test_valid_response(self):
        record_data = create_record(group="community")
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(record=record_data),
        )
        result = self.records_client.get()
        self.assertIsInstance(result, Record)
        self.assertEqual(
            result.ciim_id,
            record_data["@template"]["details"]["ciimId"],
        )
        self.assertEqual(
            result.description,
            record_data["@template"]["details"]["description"],
        )

    @responses.activate
    def test_raises_doesnotexist_when_no_results_received(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(status_code=404),
        )
        with self.assertRaises(DoesNotExist):
            self.records_client.get()

    @responses.activate
    def test_raises_multipleobjectsreturned_when_multiple_results_received(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_search_response(records=[create_record(), create_record()]),
        )
        with self.assertRaises(MultipleObjectsReturned):
            self.records_client.get()


class TestClientSearchReponse(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()

    @responses.activate
    def test_raises_client_api_error_with_message(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json={"message": "failure to get a peer from the ring-balancer"},
            status=503,
        )

        with self.assertRaisesMessage(
            ClientAPIServiceUnavailableError,
            "failure to get a peer from the ring-balancer",
        ):
            self.records_client.search()

    @responses.activate
    def test_raises_client_api_error_on_elastic_search_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json={
                "error": {
                    "root_cause": [],
                    "type": "search_phase_execution_exception",
                    "reason": "all shards failed",
                    "phase": "query",
                    "grouped": True,
                    "failed_shards": [],
                },
                "status": 503,
            },
            status=503,
        )

        with self.assertRaisesMessage(
            ClientAPIServiceUnavailableError, "all shards failed"
        ):
            self.records_client.search()

    @responses.activate
    def test_raises_client_api_error_on_java_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json={
                "timestamp": "2021-08-26T09:07:31.688+00:00",
                "status": 400,
                "error": "Bad Request",
                "message": (
                    "Failed to convert value of type 'java.lang.String' "
                    "to required type 'java.lang.Integer'; "
                    "nested exception is java.lang.NumberFormatException: "
                    'For input string: "999999999999999999"'
                ),
                "path": "/search",
            },
            status=400,
        )

        with self.assertRaisesMessage(
            ClientAPIBadRequestError, "Failed to convert value of type"
        ):
            self.records_client.search()

    @responses.activate
    def test_internal_server_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json={
                "message": ("Internal Server Error"),
            },
            status=500,
        )

        with self.assertRaisesMessage(
            ClientAPIInternalServerError, "Internal Server Error"
        ):
            self.records_client.search()

    @responses.activate
    def test_default_exception(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json={
                "message": ("I'm a teapot"),
            },
            status=418,
        )

        with self.assertRaisesMessage(ClientAPICommunicationError, "I'm a teapot"):
            self.records_client.search()

    @responses.activate
    def test_valid_response_multiple_records(self):
        # TODO:Rosetta - tna, nonTna
        # TODO:Rosetta - community bucket
        # bucket_counts_response = {
        #     "took": 85,
        #     "timed_out": False,
        #     "_shards": {
        #         "total": 2,
        #         "successful": 2,
        #         "skipped": 0,
        #         "failed": 0,
        #     },
        #     "aggregations": {"groups": {"buckets": []}},
        # }
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json=create_search_response(
                records=[
                    create_record(group="community", ciim_id="swop-49209"),
                    create_record(group="community", ciim_id="wmk-16758"),
                ]
            ),
            # TODO:Rosetta
            # json={
            #     "responses": [
            #         bucket_counts_response,
            #         {
            #             "took": 85,
            #             "timed_out": False,
            #             "_shards": {
            #                 "total": 2,
            #                 "successful": 2,
            #                 "skipped": 0,
            #                 "failed": 0,
            #             },
            #             "aggregations": {},
            #             "hits": {
            #                 "total": {"value": 0, "relation": "eq"},
            #                 "max_score": 14.217057,
            #                 "hits": [],
            #             },
            #         },
            #     ]
            # },
        )
        response = self.records_client.search()
        self.assertIsInstance(response, ResultList)
        # TODO:Rosetta
        # self.assertFalse(response.bucket_counts)
        self.assertEqual(len(response.hits), 2)
        self.assertTrue(isinstance(response.hits[0], Record))
        self.assertTrue(isinstance(response.hits[1], Record))
        self.assertEqual(response.hits[0].ciim_id, "swop-49209")
        self.assertEqual(response.hits[1].ciim_id, "wmk-16758")


@unittest.skip("TODO: Keep, not in scope for Ohos-Etna at this time")
class TestClientFetchAllReponse(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()

    @responses.activate
    def test_raises_client_api_error_with_message(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetchAll",
            json={"message": "failure to get a peer from the ring-balancer"},
            status=503,
        )

        with self.assertRaisesMessage(
            ClientAPIServiceUnavailableError,
            "failure to get a peer from the ring-balancer",
        ):
            self.records_client.fetch_all()

    @responses.activate
    def test_raises_client_api_error_on_elastic_fetchAll_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetchAll",
            json={
                "error": {
                    "root_cause": [],
                    "type": "fetchAll_phase_execution_exception",
                    "reason": "all shards failed",
                    "phase": "query",
                    "grouped": True,
                    "failed_shards": [],
                },
                "status": 503,
            },
            status=503,
        )

        with self.assertRaisesMessage(
            ClientAPIServiceUnavailableError, "all shards failed"
        ):
            self.records_client.fetch_all()

    @responses.activate
    def test_raises_client_api_error_on_java_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetchAll",
            json={
                "timestamp": "2021-08-26T09:07:31.688+00:00",
                "status": 400,
                "error": "Bad Request",
                "message": (
                    "Failed to convert value of type 'java.lang.String' "
                    "to required type 'java.lang.Integer'; "
                    "nested exception is java.lang.NumberFormatException: "
                    'For input string: "999999999999999999"'
                ),
                "path": "/fetchAll",
            },
            status=400,
        )

        with self.assertRaisesMessage(
            ClientAPIBadRequestError, "Failed to convert value of type"
        ):
            self.records_client.fetch_all()

    @responses.activate
    def test_internal_server_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetchAll",
            json={
                "message": ("Internal Server Error"),
            },
            status=500,
        )

        with self.assertRaisesMessage(
            ClientAPIInternalServerError, "Internal Server Error"
        ):
            self.records_client.fetch_all()

    @responses.activate
    def test_default_exception(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetchAll",
            json={
                "message": ("I'm a teapot"),
            },
            status=418,
        )

        with self.assertRaisesMessage(ClientAPICommunicationError, "I'm a teapot"):
            self.records_client.fetch_all()

    @responses.activate
    def test_valid_response(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetchAll",
            json={
                "took": 85,
                "timed_out": False,
                "_shards": {"total": 2, "successful": 2, "skipped": 0, "failed": 0},
                "hits": {
                    "total": {"value": 0, "relation": "eq"},
                    "max_score": 14.217057,
                    "hits": [],
                },
            },
        )
        response = self.records_client.fetch_all()
        self.assertIsInstance(response, ResultList)
        self.assertEqual(response.hits, ())
