from django.test import SimpleTestCase

import responses

from ..client import KongClient, SortBy, SortOrder, Stream, Template
from ..exceptions import KongError


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
    def test_with_keyword(self):
        self.client.search(keyword="Egypt")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?keyword=Egypt",
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
            "https://kong.test/data/search?sort=date_created",
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
    def test_with_show_buckets_true(self):
        self.client.search(show_buckets=True)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?showBuckets=True",
        )

    @responses.activate
    def test_with_show_buckets_false(self):
        self.client.search(show_buckets=False)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?showBuckets=False",
        )

    @responses.activate
    def test_with_buckets(self):
        self.client.search(buckets=["bucket-one", "bucket-two", "bucket-three"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?buckets=bucket-one%2C+bucket-two%2C+bucket-three",
        )

    @responses.activate
    def test_with_topics(self):
        self.client.search(topics=["topic-one", "topic-two", "topic-three"])

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?topics=topic-one%2C+topic-two%2C+topic-three",
        )

    @responses.activate
    def test_with_references(self):
        self.client.search(
            references=["reference-one", "reference-two", "reference-three"]
        )

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?references=reference-one%2C+reference-two%2C+reference-three",
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
            KongError, "failure to get a peer from the ring-balancer"
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

        with self.assertRaisesMessage(KongError, "all shards failed"):
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

        with self.assertRaisesMessage(KongError, "Failed to convert value of type"):
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
            KongError, "failure to get a peer from the ring-balancer"
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

        with self.assertRaisesMessage(KongError, "all shards failed"):
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

        with self.assertRaisesMessage(KongError, "Failed to convert value of type"):
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
            KongError, "failure to get a peer from the ring-balancer"
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

        with self.assertRaisesMessage(KongError, "all shards failed"):
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

        with self.assertRaisesMessage(KongError, "Failed to convert value of type"):
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
