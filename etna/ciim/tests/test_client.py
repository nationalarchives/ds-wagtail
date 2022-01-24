from django.test import TestCase

import responses

from ..client import KongClient
from ..exceptions import InvalidResponse, KongError, KubernetesError


class ClientSearchTest(TestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

        responses.add(responses.GET, "https://kong.test/data/search", json={})

    @responses.activate
    def test_default_parameters(self):
        self.client.search()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?from=0",
        )

    @responses.activate
    def test_from_paramter_conversion(self):
        self.client.search(start=10)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?from=10",
        )

    @responses.activate
    def test_search_with_reference_number(self):
        self.client.search(reference_number="ADM 223/3")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?term=ADM+223%2F3&from=0",
        )

    @responses.activate
    def test_search_with_iaid(self):
        self.client.search(iaid="C10297")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?term=C10297&from=0",
        )

    @responses.activate
    def test_search_with_term(self):
        self.client.search(term="Egypt")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/search?term=Egypt&from=0",
        )


class ClientFetchTest(TestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

        responses.add(responses.GET, "https://kong.test/data/fetch", json={})

    @responses.activate
    def test_default_parameters(self):

        self.client.fetch()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?from=0&expand=false",
        )

    @responses.activate
    def test_reference_number_conversion(self):
        self.client.fetch(reference_number="PROD 1/4")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?ref=PROD+1%2F4&from=0&expand=false",
        )

    @responses.activate
    def test_expand_parameter_conversion_true(self):
        self.client.fetch(expand=True)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?from=0&expand=true",
        )

    @responses.activate
    def test_expand_parameter_conversion_false(self):
        self.client.fetch(expand=False)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?from=0&expand=false",
        )

    @responses.activate
    def test_fetch_with_iaid(self):
        self.client.fetch(iaid="C198022")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/data/fetch?iaid=C198022&from=0&expand=false",
        )


class TestClientFetchReponse(TestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

    @responses.activate
    def test_test_mode_doesnt_use_requests(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            status=500,
        )

        with self.assertRaises(InvalidResponse):
            self.client.fetch()

    @responses.activate
    def test_raises_kubernetes_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json={"message": "failure to get a peer from the ring-balancer"},
        )

        with self.assertRaises(KubernetesError):
            self.client.fetch()

    @responses.activate
    def test_raises_kong_error(self):
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
        )

        with self.assertRaises(KongError):
            self.client.fetch()

    @responses.activate
    def test_raises_java_error(self):
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
                    "For input string: \"999999999999999999\""
                ),
                "path": "/search",
            },
            status=400,
        )

        with self.assertRaises(InvalidResponse):
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


class TestClientSearchReponse(TestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test", api_key="")

    @responses.activate
    def test_500_raises_invalid_response(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            status=500,
            json={},
        )

        with self.assertRaises(InvalidResponse):
            self.client.search()

    @responses.activate
    def test_500_with_reason_raises_invalid_response(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            status=500,
            json={"error": {"root_cause": [{"reason": "Test Error"}]}},
        )

        with self.assertRaisesMessage(InvalidResponse, "Reason: Test Error"):
            self.client.search()

    @responses.activate
    def test_raises_kubernetes_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json={"message": "failure to get a peer from the ring-balancer"},
        )

        with self.assertRaises(KubernetesError):
            self.client.search()

    @responses.activate
    def test_raises_kong_error(self):
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
        )

        with self.assertRaises(KongError):
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
