from unittest.mock import patch

from app.ciim.blocks import RecordChooserBlock
from django.test import SimpleTestCase


class RecordChooserBlockTests(SimpleTestCase):
    @patch("app.ciim.blocks.CIIMClient")
    def test_get_api_representation_fetches_serialized_record(self, mock_client_class):
        client = mock_client_class.return_value
        client.get_serialized_record.return_value = {
            "title": "Record title",
            "iaid": "C123",
            "reference_number": "WO 1/2/3",
        }
        block = RecordChooserBlock()

        representation = block.get_api_representation("C123")

        self.assertEqual(
            representation,
            {
                "title": "Record title",
                "iaid": "C123",
                "reference_number": "WO 1/2/3",
            },
        )
        mock_client_class.assert_called_once_with(params={"id": "C123"})
        client.get_serialized_record.assert_called_once_with()
