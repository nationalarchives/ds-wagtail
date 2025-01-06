from datetime import datetime

import responses
from django.conf import settings
from django.test import SimpleTestCase

from etna.ciim.constants import Aggregation
from etna.ciim.tests.factories import (
    create_record,
    create_response,
    create_search_response,
)
from etna.records.api import get_records_client
from etna.records.models import Record

from ..client import ResultList, SortBy, SortOrder, Stream, Template
from ..exceptions import (
    ClientAPIBadRequestError,
    ClientAPICommunicationError,
    ClientAPIInternalServerError,
    ClientAPIServiceUnavailableError,
    DoesNotExist,
    MultipleObjectsReturned,
)


class ClientSearchAllTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.records_client = get_records_client()

    def setUp(self):
        responses.add(
            responses.GET, f"{settings.CLIENT_BASE_URL}/searchAll", json={}
        )

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.records_client.search_all()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchAll",
        )

    @responses.activate
    def test_with_q(self):
        self.records_client.search_all(q="Egypt")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchAll?q=Egypt",
        )

    @responses.activate
    def test_with_template_details(self):
        self.records_client.search_all(template=Template.DETAILS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchAll?template=details",
        )

    @responses.activate
    def test_with_template_results(self):
        self.records_client.search_all(template=Template.RESULTS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchAll?template=results",
        )

    @responses.activate
    def test_with_aggregations(self):
        self.records_client.search_all(
            aggregations=[Aggregation.LEVEL, Aggregation.COLLECTION]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchAll?"
            "aggregations=level"
            "&aggregations=collection",
        )

    @responses.activate
    def test_with_filter_aggregations(self):
        self.records_client.search_all(
            filter_aggregations=[
                "level:Item",
                "topic:second world war",
                "closure:Closed Or Retained Document, Closed Description",
            ]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                f"{settings.CLIENT_BASE_URL}/searchAll"
                "?filterAggregations=level%3AItem"
                "&filterAggregations=topic%3Asecond+world+war"
                "&filterAggregations=closure%3AClosed+Or+Retained+Document%2C+Closed+Description"
            ),
        )

    @responses.activate
    def test_with_offset(self):
        self.records_client.search_all(offset=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchAll?from=20",
        )

    @responses.activate
    def test_with_size(self):
        self.records_client.search_all(size=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchAll?size=20",
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

    @responses.activate
    def test_with_web_reference(self):
        self.records_client.search(web_reference="ADM/223/3")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?webReference=ADM%2F223%2F3",
        )

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

    @responses.activate
    def test_with_opening_end_date(self):
        self.records_client.search(
            opening_end_date=datetime(year=1901, month=2, day=3)
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?openingEndDate=1901-02-03T00%3A00%3A00",
        )

    @responses.activate
    def test_with_created_start_date(self):
        self.records_client.search(
            created_start_date=datetime(year=1901, month=2, day=3)
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?createdStartDate=1901-02-03T00%3A00%3A00",
        )

    @responses.activate
    def test_with_created_end_date(self):
        self.records_client.search(
            created_end_date=datetime(year=1901, month=2, day=3)
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?createdEndDate=1901-02-03T00%3A00%3A00",
        )

    @responses.activate
    def test_with_evidential_stream(self):
        self.records_client.search(stream=Stream.EVIDENTIAL)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?stream=evidential",
        )

    @responses.activate
    def test_with_interpretive_stream(self):
        self.records_client.search(stream=Stream.INTERPRETIVE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?stream=interpretive",
        )

    @responses.activate
    def test_with_sort_title(self):
        self.records_client.search(sort_by=SortBy.TITLE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?sort=title",
        )

    @responses.activate
    def test_with_sort_date_created(self):
        self.records_client.search(sort_by=SortBy.DATE_CREATED)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?sort=dateCreated",
        )

    @responses.activate
    def test_with_sort_date_opening(self):
        self.records_client.search(sort_by=SortBy.DATE_OPENING)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?sort=dateOpening",
        )

    @responses.activate
    def test_with_sort_relevance(self):
        self.records_client.search(sort_by=SortBy.RELEVANCE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?sort=",
        )

    @responses.activate
    def test_with_sort_order_asc(self):
        self.records_client.search(sort_order=SortOrder.ASC)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?sortOrder=asc",
        )

    @responses.activate
    def test_with_sort_order_desc(self):
        self.records_client.search(sort_order=SortOrder.DESC)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?sortOrder=desc",
        )

    @responses.activate
    def test_with_template_details(self):
        self.records_client.search(template=Template.DETAILS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?template=details",
        )

    @responses.activate
    def test_with_template_results(self):
        self.records_client.search(template=Template.RESULTS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?template=results",
        )

    @responses.activate
    def test_with_aggregations(self):
        self.records_client.search(
            aggregations=[
                Aggregation.LEVEL,
                Aggregation.COLLECTION,
                Aggregation.TYPE,
            ]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?"
            "aggregations=level"
            "&aggregations=collection"
            "&aggregations=type",
        )

    @responses.activate
    def test_with_filter_aggregations(self):
        self.records_client.search(
            filter_aggregations=[
                "level:Item",
                "topic:second world war",
                "closure:Closed Or Retained Document, Closed Description",
            ]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?"
            "filterAggregations=level%3AItem"
            "&filterAggregations=topic%3Asecond+world+war"
            "&filterAggregations=closure%3AClosed+Or+Retained+Document%2C+Closed+Description",
        )

    @responses.activate
    def test_with_filter_collection(self):
        self.records_client.search(
            filter_aggregations=["collection:IR", "collection:PROB"]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?"
            "filterAggregations=collection%3AIR%3Aor&"
            "filterAggregations=collection%3APROB%3Aor",
        )

    @responses.activate
    def test_with_filter_held_by_without_special_chars(self):
        self.records_client.search(
            filter_aggregations=["heldBy:Tate Gallery Archive"]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?filterAggregations=heldBy%3ATate+Gallery+Archive",
        )

    @responses.activate
    def test_with_filter_held_by_with_special_chars(self):
        self.records_client.search(
            filter_aggregations=[
                "heldBy:1/ 2( 3) 4: 5, 6& 7- 8| 9+ 10@ 11! 12."
            ]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?filterAggregations=heldBy%3A1+2+3+4+5+6+7+8+9+10+11+12+",
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
            "filterAggregations=heldBy%3ARolls+Royce+plc%3Aor&"
            "filterAggregations=heldBy%3AIRIE+dance+theatre%3Aor&"
            "filterAggregations=heldBy%3ARoyal+Yorkshire+Lodge+No+265%3Aor&"
            "filterAggregations=heldBy%3AREWIND+Artists%27+Video+in+the+70s+80s%3Aor&"
            "filterAggregations=heldBy%3ANational+Arts+Education+Archive+YSP%3Aor&"
            "filterAggregations=heldBy%3AFoster+Partners%3Aor&"
            "filterAggregations=heldBy%3ALabour+History+Archive+and+Study+Centre+People%27s+History+Museum+University+of+Central+Lancashire+%3Aor&"
            "filterAggregations=heldBy%3ALondon+University+London+School+of+Economics+The+Women%27s+Library%3Aor",
        )

    @responses.activate
    def test_with_filter_held_by_with_special_chars_not_prepared(self):
        self.records_client.search(filter_aggregations=["heldBy:People's"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?filterAggregations=heldBy%3APeople%27s",
        )

    @responses.activate
    def test_with_filter_level(self):
        self.records_client.search(
            filter_aggregations=["level:Item", "level:Piece"]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/search?"
            "filterAggregations=level%3AItem%3Aor&"
            "filterAggregations=level%3APiece%3Aor",
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
            "filterAggregations=type%3Aperson&"
            "filterAggregations=type%3Aorganisation",
        )

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
    def test_with_template_details(self):
        self.records_client.search_unified(template=Template.DETAILS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?template=details",
        )

    @responses.activate
    def test_with_template_results(self):
        self.records_client.search_unified(template=Template.RESULTS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?template=results",
        )

    @responses.activate
    def test_with_sort_title(self):
        self.records_client.search_unified(sort_by=SortBy.TITLE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sort=title",
        )

    @responses.activate
    def test_with_sort_date_created(self):
        self.records_client.search_unified(sort_by=SortBy.DATE_CREATED)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sort=dateCreated",
        )

    @responses.activate
    def test_with_sort_date_opening(self):
        self.records_client.search_unified(sort_by=SortBy.DATE_OPENING)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sort=dateOpening",
        )

    @responses.activate
    def test_with_sort_relevance(self):
        self.records_client.search_unified(sort_by=SortBy.RELEVANCE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sort=",
        )

    @responses.activate
    def test_with_sort_order_asc(self):
        self.records_client.search_unified(sort_order=SortOrder.ASC)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/searchUnified?sortOrder=asc",
        )

    @responses.activate
    def test_with_sort_order_desc(self):
        self.records_client.search_unified(sort_order=SortOrder.DESC)

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
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json=create_response(records=[create_record()]),
        )

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.records_client.fetch()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url, f"{settings.CLIENT_BASE_URL}/fetch"
        )

    @responses.activate
    def test_with_iaid(self):
        self.records_client.fetch(iaid="C198022")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetch?metadataId=C198022",
        )

    @responses.activate
    def test_with_id(self):
        self.records_client.fetch(id="ADM 223/3")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetch?id=ADM+223%2F3",
        )

    @responses.activate
    def test_with_template_details(self):
        self.records_client.fetch(template=Template.DETAILS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetch?template=details",
        )

    @responses.activate
    def test_with_template_results(self):
        self.records_client.fetch(template=Template.RESULTS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetch?template=results",
        )

    @responses.activate
    def test_with_expand_true(self):
        self.records_client.fetch(expand=True)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetch?expand=True",
        )

    @responses.activate
    def test_with_expand_false(self):
        self.records_client.fetch(expand=False)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetch?expand=False",
        )


class ClientFetchAllTest(SimpleTestCase):
    def setUp(self):
        self.records_client = get_records_client()
        responses.add(
            responses.GET, f"{settings.CLIENT_BASE_URL}/fetchAll", json={}
        )

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.records_client.fetch_all()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetchAll",
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
        self.records_client.fetch_all(
            iaids=["iaid-one", "iaid-two", "iaid-three"]
        )

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
            f"{settings.CLIENT_BASE_URL}/fetch",
            json={"message": "failure to get a peer from the ring-balancer"},
            status=503,
        )

        with self.assertRaisesMessage(
            ClientAPIServiceUnavailableError,
            "failure to get a peer from the ring-balancer",
        ):
            self.records_client.fetch()

    @responses.activate
    def test_raises_client_api_error_on_elastic_search_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
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
            self.records_client.fetch()

    @responses.activate
    def test_raises_client_api_error_on_java_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
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
                "path": "/fetch",
            },
            status=400,
        )

        with self.assertRaisesMessage(
            ClientAPIBadRequestError, "Failed to convert value of type"
        ):
            self.records_client.fetch()

    @responses.activate
    def test_internal_server_error(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json={
                "message": ("Internal Server Error"),
            },
            status=500,
        )

        with self.assertRaisesMessage(
            ClientAPIInternalServerError, "Internal Server Error"
        ):
            self.records_client.fetch()

    @responses.activate
    def test_default_exception(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json={
                "message": ("I'm a teapot"),
            },
            status=418,
        )

        with self.assertRaisesMessage(
            ClientAPICommunicationError, "I'm a teapot"
        ):
            self.records_client.fetch()

    @responses.activate
    def test_valid_response(self):
        record_data = create_record()
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json=create_response(records=[record_data]),
        )
        result = self.records_client.fetch()
        self.assertIsInstance(result, Record)
        self.assertEqual(
            result.reference_number,
            record_data["_source"]["identifier"][1]["reference_number"],
        )

    @responses.activate
    def test_raises_doesnotexist_when_no_results_received(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json=create_response(records=[]),
        )
        with self.assertRaises(DoesNotExist):
            self.records_client.fetch()

    @responses.activate
    def test_raises_multipleobjectsreturned_when_multiple_results_received(
        self,
    ):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json=create_response(records=[create_record(), create_record()]),
        )
        with self.assertRaises(MultipleObjectsReturned):
            self.records_client.fetch()


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

        with self.assertRaisesMessage(
            ClientAPICommunicationError, "I'm a teapot"
        ):
            self.records_client.search()

    @responses.activate
    def test_valid_response(self):
        bucket_counts_response = {
            "took": 85,
            "timed_out": False,
            "_shards": {
                "total": 2,
                "successful": 2,
                "skipped": 0,
                "failed": 0,
            },
            "aggregations": {"groups": {"buckets": []}},
        }
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json={
                "responses": [
                    bucket_counts_response,
                    {
                        "took": 85,
                        "timed_out": False,
                        "_shards": {
                            "total": 2,
                            "successful": 2,
                            "skipped": 0,
                            "failed": 0,
                        },
                        "aggregations": {},
                        "hits": {
                            "total": {"value": 0, "relation": "eq"},
                            "max_score": 14.217057,
                            "hits": [],
                        },
                    },
                ]
            },
        )
        response = self.records_client.search()
        self.assertIsInstance(response, ResultList)
        self.assertFalse(response.bucket_counts)
        self.assertEqual(response.hits, ())


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

        with self.assertRaisesMessage(
            ClientAPICommunicationError, "I'm a teapot"
        ):
            self.records_client.fetch_all()

    @responses.activate
    def test_valid_response(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetchAll",
            json={
                "took": 85,
                "timed_out": False,
                "_shards": {
                    "total": 2,
                    "successful": 2,
                    "skipped": 0,
                    "failed": 0,
                },
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
