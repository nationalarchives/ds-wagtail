from datetime import datetime

from django.test import SimpleTestCase

import responses

from ..client import Aggregation, KongClient, SortBy, SortOrder, Stream, Template
from ..exceptions import (
    KongBadRequestError,
    KongCommunicationError,
    KongInternalServerError,
    KongServiceUnavailableError,
)


class ClientSearchAllTest(SimpleTestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

        responses.add(responses.GET, "https://kong.test/data/searchAll", json={})

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.client.search_all()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url, "https://kong.test/data/searchAll"
        )

    @responses.activate
    def test_with_q(self):
        self.client.search_all(q="Egypt")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchAll?q=Egypt",
        )

    @responses.activate
    def test_with_template_details(self):
        self.client.search_all(template=Template.DETAILS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchAll?template=details",
        )

    @responses.activate
    def test_with_template_results(self):
        self.client.search_all(template=Template.RESULTS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchAll?template=results",
        )

    @responses.activate
    def test_with_aggregations(self):
        self.client.search_all(aggregations=[Aggregation.LEVEL, Aggregation.COLLECTION])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchAll?aggregations=level%2C+collection",
        )

    @responses.activate
    def test_with_filter_aggregations(self):
        self.client.search_all(
            filter_aggregations=[
                "level:Item",
                "topic:second world war",
                # Comma should be stripped if included in filterParameter
                "closureStatus:Closed Or Retained Document, Closed Description",
            ]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            (
                "https://kong.test/data/searchAll"
                "?filterAggregations=level%3AItem%2C+topic%3Asecond+world+war%2C+closureStatus%3AClosed+Or+Retained+Document++Closed+Description"
            ),
        )

    @responses.activate
    def test_with_offset(self):
        self.client.search_all(offset=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchAll?from=20",
        )

    @responses.activate
    def test_with_size(self):
        self.client.search_all(size=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchAll?size=20",
        )


class ClientSearchTest(SimpleTestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

        responses.add(responses.GET, "https://kong.test/data/search", json={})

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.client.search()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url, "https://kong.test/data/search"
        )

    @responses.activate
    def test_with_q(self):
        self.client.search(q="Egypt")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?q=Egypt",
        )

    @responses.activate
    def test_with_web_reference(self):
        self.client.search(web_reference="ADM/223/3")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?webReference=ADM%2F223%2F3",
        )

    @responses.activate
    def test_with_opening_start_date(self):
        self.client.search(opening_start_date=datetime(year=1901, month=2, day=3))

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?openingStartDate=1901-02-03T00%3A00%3A00",
        )

    @responses.activate
    def test_with_opening_end_date(self):
        self.client.search(opening_end_date=datetime(year=1901, month=2, day=3))

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?openingEndDate=1901-02-03T00%3A00%3A00",
        )

    @responses.activate
    def test_with_created_start_date(self):
        self.client.search(created_start_date=datetime(year=1901, month=2, day=3))

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?createdStartDate=1901-02-03T00%3A00%3A00",
        )

    @responses.activate
    def test_with_created_end_date(self):
        self.client.search(created_end_date=datetime(year=1901, month=2, day=3))

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?createdEndDate=1901-02-03T00%3A00%3A00",
        )

    @responses.activate
    def test_with_evidential_stream(self):
        self.client.search(stream=Stream.EVIDENTIAL)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?stream=evidential",
        )

    @responses.activate
    def test_with_interpretive_stream(self):
        self.client.search(stream=Stream.INTERPRETIVE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?stream=interpretive",
        )

    @responses.activate
    def test_with_sort_title(self):
        self.client.search(sort_by=SortBy.TITLE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?sort=title",
        )

    @responses.activate
    def test_with_sort_date_created(self):
        self.client.search(sort_by=SortBy.DATE_CREATED)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?sort=dateCreated",
        )

    @responses.activate
    def test_with_sort_date_opening(self):
        self.client.search(sort_by=SortBy.DATE_OPENING)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?sort=dateOpening",
        )

    @responses.activate
    def test_with_sort_relevance(self):
        self.client.search(sort_by=SortBy.RELEVANCE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?sort=",
        )

    @responses.activate
    def test_with_sort_order_asc(self):
        self.client.search(sort_order=SortOrder.ASC)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?sortOrder=asc",
        )

    @responses.activate
    def test_with_sort_order_desc(self):
        self.client.search(sort_order=SortOrder.DESC)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?sortOrder=desc",
        )

    @responses.activate
    def test_with_template_details(self):
        self.client.search(template=Template.DETAILS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?template=details",
        )

    @responses.activate
    def test_with_template_results(self):
        self.client.search(template=Template.RESULTS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?template=results",
        )

    @responses.activate
    def test_with_aggregations(self):
        self.client.search(aggregations=[Aggregation.LEVEL, Aggregation.COLLECTION])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?aggregations=level%2C+collection",
        )

    @responses.activate
    def test_with_filter_aggregations(self):
        self.client.search(filter_aggregations=["level:Item", "topic:second world war"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?filterAggregations=level%3AItem%2C+topic%3Asecond+world+war",
        )

    @responses.activate
    def test_with_filter_held_by_without_special_chars(self):
        self.client.search(filter_aggregations=["heldBy:Tate Gallery Archive"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?filterAggregations=heldBy%3ATate+Gallery+Archive",
        )

    @responses.activate
    def test_with_filter_held_by_with_special_chars(self):
        self.client.search(filter_aggregations=["heldBy: 1\2/3:4,5&(People's)"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?filterAggregations=heldBy%3A+1%02+3+4+5++People%27s+",
        )

    @responses.activate
    def test_with_filter_keyword(self):
        self.client.search(filter_keyword="filter keyword")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?filter=filter+keyword",
        )

    @responses.activate
    def test_with_offset(self):
        self.client.search(offset=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?from=20",
        )

    @responses.activate
    def test_with_size(self):
        self.client.search(size=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?size=20",
        )


class ClientSearchUnifiedTest(SimpleTestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

        responses.add(responses.GET, "https://kong.test/data/searchUnified", json={})

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.client.search_unified()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url, "https://kong.test/data/searchUnified"
        )

    @responses.activate
    def test_with_q(self):
        self.client.search_unified(q="Egypt")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?q=Egypt",
        )

    @responses.activate
    def test_with_web_reference(self):
        self.client.search_unified(web_reference="ADM/223/3")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?webReference=ADM%2F223%2F3",
        )

    @responses.activate
    def test_with_evidential_stream(self):
        self.client.search_unified(stream=Stream.EVIDENTIAL)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?stream=evidential",
        )

    @responses.activate
    def test_with_interpretive_stream(self):
        self.client.search_unified(stream=Stream.INTERPRETIVE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?stream=interpretive",
        )

    @responses.activate
    def test_with_template_details(self):
        self.client.search_unified(template=Template.DETAILS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?template=details",
        )

    @responses.activate
    def test_with_template_results(self):
        self.client.search_unified(template=Template.RESULTS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?template=results",
        )

    @responses.activate
    def test_with_sort_title(self):
        self.client.search_unified(sort_by=SortBy.TITLE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?sort=title",
        )

    @responses.activate
    def test_with_sort_date_created(self):
        self.client.search_unified(sort_by=SortBy.DATE_CREATED)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?sort=dateCreated",
        )

    @responses.activate
    def test_with_sort_date_opening(self):
        self.client.search_unified(sort_by=SortBy.DATE_OPENING)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?sort=dateOpening",
        )

    @responses.activate
    def test_with_sort_relevance(self):
        self.client.search_unified(sort_by=SortBy.RELEVANCE)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?sort=",
        )

    @responses.activate
    def test_with_sort_order_asc(self):
        self.client.search_unified(sort_order=SortOrder.ASC)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?sortOrder=asc",
        )

    @responses.activate
    def test_with_sort_order_desc(self):
        self.client.search_unified(sort_order=SortOrder.DESC)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?sortOrder=desc",
        )

    @responses.activate
    def test_with_offset(self):
        self.client.search_unified(offset=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?from=20",
        )

    @responses.activate
    def test_with_size(self):
        self.client.search_unified(size=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/searchUnified?size=20",
        )


class ClientFetchTest(SimpleTestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

        responses.add(responses.GET, "https://kong.test/data/fetch", json={})

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.client.fetch()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.url, "https://kong.test/data/fetch")

    @responses.activate
    def test_with_iaid(self):
        self.client.fetch(iaid="C198022")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?iaid=C198022",
        )

    @responses.activate
    def test_with_id(self):
        self.client.fetch(id="ADM 223/3")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?id=ADM+223%2F3",
        )

    @responses.activate
    def test_with_template_details(self):
        self.client.fetch(template=Template.DETAILS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?template=details",
        )

    @responses.activate
    def test_with_template_results(self):
        self.client.fetch(template=Template.RESULTS)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?template=results",
        )

    @responses.activate
    def test_with_expand_true(self):
        self.client.fetch(expand=True)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?expand=True",
        )

    @responses.activate
    def test_with_expand_false(self):
        self.client.fetch(expand=False)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?expand=False",
        )


class ClientFetchAllTest(SimpleTestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

        responses.add(responses.GET, "https://kong.test/data/fetchAll", json={})

    @responses.activate
    def test_no_arguments_makes_request_with_no_parameters(self):
        self.client.fetch_all()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url, "https://kong.test/data/fetchAll"
        )

    @responses.activate
    def test_with_ids(self):
        self.client.fetch_all(ids=["id-one", "id-two", "id-three"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetchAll?ids=id-one%2C+id-two%2C+id-three",
        )

    @responses.activate
    def test_with_iaids(self):
        self.client.fetch_all(iaids=["iaid-one", "iaid-two", "iaid-three"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetchAll?iaids=iaid-one%2C+iaid-two%2C+iaid-three",
        )

    @responses.activate
    def test_with_rid(self):
        self.client.fetch_all(rid="rid-123")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetchAll?rid=rid-123",
        )

    @responses.activate
    def test_with_size(self):
        self.client.fetch_all(size=20)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetchAll?size=20",
        )


class TestClientFetchReponse(SimpleTestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

    @responses.activate
    def test_raises_kong_error_with_message(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json={"message": "failure to get a peer from the ring-balancer"},
            status=503,
        )

        with self.assertRaisesMessage(
            KongServiceUnavailableError, "failure to get a peer from the ring-balancer"
        ):
            self.client.fetch()

    @responses.activate
    def test_raises_kong_error_on_elastic_search_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
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

        with self.assertRaisesMessage(KongServiceUnavailableError, "all shards failed"):
            self.client.fetch()

    @responses.activate
    def test_raises_kong_error_on_java_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
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
            KongBadRequestError, "Failed to convert value of type"
        ):
            self.client.fetch()

    @responses.activate
    def test_internal_server_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json={
                "message": ("Internal Server Error"),
            },
            status=500,
        )

        with self.assertRaisesMessage(KongInternalServerError, "Internal Server Error"):
            self.client.fetch()

    @responses.activate
    def test_default_exception(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json={
                "message": ("I'm a teapot"),
            },
            status=418,
        )

        with self.assertRaisesMessage(KongCommunicationError, "I'm a teapot"):
            self.client.fetch()

    @responses.activate
    def test_valid_response(self):
        valid_response = {
            "took": 85,
            "timed_out": False,
            "_shards": {"total": 2, "successful": 2, "skipped": 0, "failed": 0},
            "hits": {
                "total": {"value": 0, "relation": "eq"},
                "max_score": 14.217057,
                "hits": [],
            },
        }

        responses.add(
            responses.GET, "https://kong.test/data/fetch", json=valid_response
        )

        response = self.client.fetch()

        self.assertEqual(response, valid_response)


class TestClientSearchReponse(SimpleTestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

    @responses.activate
    def test_raises_kong_error_with_message(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json={"message": "failure to get a peer from the ring-balancer"},
            status=503,
        )

        with self.assertRaisesMessage(
            KongServiceUnavailableError, "failure to get a peer from the ring-balancer"
        ):
            self.client.search()

    @responses.activate
    def test_raises_kong_error_on_elastic_search_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
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

        with self.assertRaisesMessage(KongServiceUnavailableError, "all shards failed"):
            self.client.search()

    @responses.activate
    def test_raises_kong_error_on_java_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
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
            KongBadRequestError, "Failed to convert value of type"
        ):
            self.client.search()

    @responses.activate
    def test_internal_server_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json={
                "message": ("Internal Server Error"),
            },
            status=500,
        )

        with self.assertRaisesMessage(KongInternalServerError, "Internal Server Error"):
            self.client.search()

    @responses.activate
    def test_default_exception(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json={
                "message": ("I'm a teapot"),
            },
            status=418,
        )

        with self.assertRaisesMessage(KongCommunicationError, "I'm a teapot"):
            self.client.search()

    @responses.activate
    def test_valid_response(self):
        valid_response = {
            "took": 85,
            "timed_out": False,
            "_shards": {"total": 2, "successful": 2, "skipped": 0, "failed": 0},
            "hits": {
                "total": {"value": 0, "relation": "eq"},
                "max_score": 14.217057,
                "hits": [],
            },
        }

        responses.add(
            responses.GET, "https://kong.test/data/search", json=valid_response
        )

        response = self.client.search()

        self.assertEqual(response, valid_response)


class TestClientFetchAllReponse(SimpleTestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

    @responses.activate
    def test_raises_kong_error_with_message(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetchAll",
            json={"message": "failure to get a peer from the ring-balancer"},
            status=503,
        )

        with self.assertRaisesMessage(
            KongServiceUnavailableError, "failure to get a peer from the ring-balancer"
        ):
            self.client.fetch_all()

    @responses.activate
    def test_raises_kong_error_on_elastic_fetchAll_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetchAll",
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

        with self.assertRaisesMessage(KongServiceUnavailableError, "all shards failed"):
            self.client.fetch_all()

    @responses.activate
    def test_raises_kong_error_on_java_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetchAll",
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
            KongBadRequestError, "Failed to convert value of type"
        ):
            self.client.fetch_all()

    @responses.activate
    def test_internal_server_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetchAll",
            json={
                "message": ("Internal Server Error"),
            },
            status=500,
        )

        with self.assertRaisesMessage(KongInternalServerError, "Internal Server Error"):
            self.client.fetch_all()

    @responses.activate
    def test_default_exception(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetchAll",
            json={
                "message": ("I'm a teapot"),
            },
            status=418,
        )

        with self.assertRaisesMessage(KongCommunicationError, "I'm a teapot"):
            self.client.fetch_all()

    @responses.activate
    def test_valid_response(self):
        valid_response = {
            "took": 85,
            "timed_out": False,
            "_shards": {"total": 2, "successful": 2, "skipped": 0, "failed": 0},
            "hits": {
                "total": {"value": 0, "relation": "eq"},
                "max_score": 14.217057,
                "hits": [],
            },
        }

        responses.add(
            responses.GET, "https://kong.test/data/fetchAll", json=valid_response
        )

        response = self.client.fetch_all()

        self.assertEqual(response, valid_response)
