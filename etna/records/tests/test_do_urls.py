from django.conf import settings
from django.test import TestCase
import responses

from etna.records.api import get_delivery_options_client


class DeliveryOptionsApiTest(TestCase):
    def setUp(self):
        self.delivery_options_client = get_delivery_options_client()

    @responses.activate
    def test_delivery_options_api_valid_call_with_iaid(self):
        # Mock the API response
        return_value = [
            {"options": 14, "surrogateLinks": [], "advancedOrderUrlParameters": None}
        ]

        iaid = "A10000"

        # Define the URL to be mocked and the response
        responses.add(
            method=responses.GET,
            url=settings.DELIVERY_OPTIONS_CLIENT_BASE_URL,
            json=return_value,
            status=200,
        )

        response = self.delivery_options_client.fetch(iaid=iaid)

        self.assertEqual(len(responses.calls), 1)

        # Assert the response data
        self.assertEqual(response, return_value)

        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.DELIVERY_OPTIONS_CLIENT_BASE_URL}?iaid={iaid}",
        )

    @responses.activate
    def test_delivery_options_api_valid_call_with_id(self):
        # Mock the API response
        return_value = [
            {"options": 14, "surrogateLinks": [], "advancedOrderUrlParameters": None}
        ]

        id = "ydydgywgd902-jij828-2718732"

        # Define the URL to be mocked and the response
        responses.add(
            method=responses.GET,
            url=settings.DELIVERY_OPTIONS_CLIENT_BASE_URL,
            json=return_value,
            status=200,
        )

        response = self.delivery_options_client.fetch(id=id)

        self.assertEqual(len(responses.calls), 1)

        # Assert the response data
        self.assertEqual(response, return_value)

        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.DELIVERY_OPTIONS_CLIENT_BASE_URL}?id={id}",
        )

    @responses.activate
    def test_delivery_options_api_call_with_invalid_parameter(self):
        # Mock the API response
        return_value = [
            {"options": 14, "surrogateLinks": [], "advancedOrderUrlParameters": None}
        ]

        unknown_parameter = "ydydgywgd902-jij828-2718732"

        # Define the URL to be mocked and the response
        responses.add(
            method=responses.GET,
            url=settings.DELIVERY_OPTIONS_CLIENT_BASE_URL,
            json=return_value,
            status=200,
        )

        with self.assertRaises(TypeError):
            response = self.delivery_options_client.fetch(
                unknown_parameter=unknown_parameter
            )

    @responses.activate
    def test_delivery_options_api_call_with_extended_payload(self):
        # Mock the API response
        return_value = [
            {
                "options": 7,
                "surrogateLinks": [
                    {
                        "xReferenceId": None,
                        "xReferenceCode": None,
                        "xReferenceName": None,
                        "xReferenceType": "DIGITIZED_DISCOVERY",
                        "xReferenceURL": '<a target="_blank" href="https://www.ancestry.co.uk/search/collections/1687/">Ancestry</a>',
                        "xReferenceDescription": None,
                        "xReferenceSortWord": None,
                    }
                ],
                "advancedOrderUrlParameters": None,
            }
        ]
        iaid = "A10000"

        # Define the URL to be mocked and the response
        responses.add(
            method=responses.GET,
            url=settings.DELIVERY_OPTIONS_CLIENT_BASE_URL,
            json=return_value,
            status=200,
        )

        response = self.delivery_options_client.fetch(iaid=iaid)

        self.assertEqual(len(responses.calls), 1)

        # Assert the response data
        self.assertEqual(response, return_value)

        self.assertEqual(
            responses.calls[0].request.url,
            f"{settings.DELIVERY_OPTIONS_CLIENT_BASE_URL}?iaid={iaid}",
        )
