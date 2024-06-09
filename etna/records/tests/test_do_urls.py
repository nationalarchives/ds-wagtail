from datetime import datetime

from django.conf import settings
from django.test import SimpleTestCase

import responses

from etna.ciim.constants import Aggregation
from etna.ciim.tests.factories import (
    create_record,
    create_response,
    create_search_response,
)
from etna.records.api import get_delivery_options_client
from etna.records.models import Record

from etna.ciim.client import ResultList, SortBy, SortOrder, Stream, Template
from etna.ciim.exceptions import (
    ClientAPIBadRequestError,
    ClientAPICommunicationError,
    ClientAPIInternalServerError,
    ClientAPIServiceUnavailableError,
    DoesNotExist,
    MultipleObjectsReturned,
)


class ClientFetchTest(SimpleTestCase):
    def setUp(self):
        self.do_record_client = get_delivery_options_client()
        x = create_response(records=[create_record()])
        print(x)
        responses.add(
            responses.GET,
            f"{settings.DELIVERY_OPTIONS_CLIENT_BASE_URL}/",
            json=create_response(records=[create_record()]),
        )

    @responses.activate
    def xtest_no_arguments_makes_request_with_no_parameters(self):
        self.do_record_client.fetch()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.url, settings.CLIENT_BASE_URL)

    @responses.activate
    def test_with_iaid(self):
        self.do_record_client.fetch(iaid="C198022")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}?iaid=C198022",
        )

    @responses.activate
    def xtest_with_id(self):
        self.do_record_client.fetch(id="ADM 223/3")

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.CLIENT_BASE_URL}/fetch?id=ADM+223%2F3",
        )


class xTestClientFetchReponse(SimpleTestCase):
    def setUp(self):
        self.do_record_client = get_delivery_options_client()

    @responses.activate
    def xtest_raises_client_api_error_with_message(self):
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
            self.do_record_client.fetch()

    @responses.activate
    def xtest_raises_client_api_error_on_elastic_search_error(self):
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
            self.do_record_client.fetch()

    @responses.activate
    def xtest_raises_client_api_error_on_java_error(self):
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
            self.do_record_client.fetch()

    @responses.activate
    def xtest_internal_server_error(self):
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
            self.do_record_client.fetch()

    @responses.activate
    def xtest_default_exception(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json={
                "message": ("I'm a teapot"),
            },
            status=418,
        )

        with self.assertRaisesMessage(ClientAPICommunicationError, "I'm a teapot"):
            self.do_record_client.fetch()

    @responses.activate
    def xtest_valid_response(self):
        record_data = create_record()
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json=create_response(records=[record_data]),
        )
        result = self.do_record_client.fetch()
        self.assertIsInstance(result, Record)
        self.assertEqual(
            result.reference_number,
            record_data["_source"]["identifier"][1]["reference_number"],
        )

    @responses.activate
    def xtest_raises_doesnotexist_when_no_results_received(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json=create_response(records=[]),
        )
        with self.assertRaises(DoesNotExist):
            self.do_record_client.fetch()

    @responses.activate
    def xtest_raises_multipleobjectsreturned_when_multiple_results_received(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/fetch",
            json=create_response(records=[create_record(), create_record()]),
        )
        with self.assertRaises(MultipleObjectsReturned):
            self.do_record_client.fetch()
