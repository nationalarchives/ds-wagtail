import unittest
from unittest.mock import patch

from etna.ciim.client import (
    DEFAULT_IAID,
    DEFAULT_REFERENCE_NUMBER,
    DEFAULT_SUMMARY_TITLE,
    CIIMClient,
)


class TestCIIMClient(unittest.TestCase):
    def setUp(self):
        self.client = CIIMClient(api_url="http://fake-api-url.com")

    @patch("etna.ciim.client.CIIMClient.get")
    def test_get_record_instance_success(self, mock_get):
        # Mock API response
        mock_get.return_value = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "summaryTitle": "Test Title",
                            "iaid": "C1234",
                            "referenceNumber": "KV 1/2/3",
                        }
                    }
                }
            ]
        }

        result = self.client.get_record_instance()
        self.assertEqual(
            result,
            {
                "summaryTitle": "Test Title",
                "iaid": "C1234",
                "referenceNumber": "KV 1/2/3",
            },
        )

    @patch("etna.ciim.client.CIIMClient.get")
    def test_get_record_instance_empty_data(self, mock_get):
        # Mock API response with empty data
        mock_get.return_value = {"data": []}

        result = self.client.get_record_instance()
        self.assertEqual(
            result,
            {
                "referenceNumber": DEFAULT_REFERENCE_NUMBER,
                "summaryTitle": DEFAULT_SUMMARY_TITLE,
                "iaid": DEFAULT_IAID,
            },
        )

    @patch("etna.ciim.client.CIIMClient.get")
    def test_get_record_list_success(self, mock_get):
        # Mock API response
        mock_get.return_value = {
            "data": [{"key": "value"}],
            "stats": {"total": 1},
        }

        results, total = self.client.get_record_list()
        self.assertEqual(results, [{"key": "value"}])
        self.assertEqual(total, 1)

    @patch("etna.ciim.client.CIIMClient.get")
    def test_get_record_list_empty(self, mock_get):
        # Mock API response with empty data
        mock_get.return_value = {"data": [], "stats": {"total": 0}}

        results, total = self.client.get_record_list()
        self.assertEqual(results, [])
        self.assertEqual(total, 0)

    @patch("etna.ciim.client.CIIMClient.get_record_instance")
    def test_get_serialized_record_success(self, mock_get_record_instance):
        # Mock the get_record_instance method
        mock_get_record_instance.return_value = {
            "summaryTitle": "Record Title",
            "iaid": "C123",
            "referenceNumber": "WO 1/2/3",
        }

        result = self.client.get_serialized_record()
        self.assertEqual(
            result,
            {
                "title": "Record Title",
                "iaid": "C123",
                "reference_number": "WO 1/2/3",
            },
        )

    @patch("etna.ciim.client.CIIMClient.get_record_instance")
    def test_get_serialized_record_empty(self, mock_get_record_instance):
        # Mock the get_record_instance method to return None
        mock_get_record_instance.return_value = None

        result = self.client.get_serialized_record()
        self.assertEqual(result, None)
