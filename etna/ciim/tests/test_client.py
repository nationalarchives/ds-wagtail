from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings

import responses

from ..client import KongClient
from ..exceptions import InvalidResponse, KubernetesError, KongError


@override_settings(KONG_CLIENT_TEST_MODE=False)
class ClientTest(TestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test")

        responses.add(responses.GET, "https://kong.test/search", json={})

    @responses.activate
    def test_default_parameters(self):

        self.client.search(start=10)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?from=10&pretty=false",
        )

    @responses.activate
    def test_from_conversion(self):
        self.client.search(start=10)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?from=10&pretty=false",
        )

    @responses.activate
    def test_pretty_parameter_conversion_true(self):
        self.client.search(pretty=True)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?from=0&pretty=true",
        )

    @responses.activate
    def test_pretty_parameter_conversion_false(self):
        self.client.search(pretty=False)

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://kong.test/search?from=0&pretty=false",
        )


class ClientReponseTest(TestCase):
    def setUp(self):
        self.client = KongClient("")


@override_settings(
    KONG_CLIENT_TEST_MODE=True,
    KONG_CLIENT_TEST_FILENAME=Path(Path(__file__).parent, "fixtures/record.json"),
)
class TestClientTestMode(TestCase):
    def setUp(self):
        self.client = KongClient("")

    def test_empty_search(self):
        self.client.search()

    def test_test_mode_doesnt_use_requests(self):
        with patch("requests.get") as mock_request:
            self.client.search()

            mock_request.assert_not_called()

    def test_test_response_returns_correct_count(self):
        response = self.client.search(term="C140")

        self.assertEqual(response["hits"]["total"]["value"], 1)

    def test_test_response_returns_correct_result(self):
        response = self.client.search(term="C140")

        self.assertEqual(
            response["hits"]["hits"][0]["_source"]["identifier"][2]["iaid"], "C140"
        )

    @override_settings(KONG_CLIENT_TEST_FILENAME="missing.json")
    def test_missing_test_file(self):
        with self.assertRaises(FileNotFoundError):
            self.client.search()


@override_settings(KONG_CLIENT_TEST_MODE=False)
class TestClientReponse(TestCase):
    def setUp(self):
        self.client = KongClient("https://kong.test")

    @responses.activate
    def test_test_mode_doesnt_use_requests(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            status=500,
        )

        with self.assertRaises(InvalidResponse):
            self.client.search()

    @responses.activate
    def test_raises_kubernetes_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json={"message": "failure to get a peer from the ring-balancer"},
        )

        with self.assertRaises(KubernetesError):
            self.client.search()

    @responses.activate
    def test_raises_kong_error(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
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
            "_shards": {
                "total": 2,
                "successful": 2,
                "skipped": 0,
                "failed": 0
            },
            "hits": {
                "total": {
                    "value": 0,
                    "relation": "eq"
                },
                "max_score": 14.217057,
                "hits": []
            }
        }

        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=valid_response
        )

        response = self.client.search()

        self.assertEqual(response, valid_response)
