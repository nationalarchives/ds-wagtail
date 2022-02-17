from django.test import SimpleTestCase

import responses

from ...ciim.exceptions import InValidResult
from ...ciim.tests.factories import create_record_no_source, create_response
from ..transforms import transform_record_result

"""inherit from SimpleTestCase to avoid creating the test_postgres """


class TransformTestCase(SimpleTestCase):
    @responses.activate
    def test_if_result_is_none_then_rais_invalid_result(self):
        with self.assertRaises(InValidResult):
            transform_record_result(None)

    @responses.activate
    def test_if_result_is_zero_lenght_then_rais_invalid_result(self):
        result = []
        with self.assertRaises(InValidResult):
            transform_record_result(result)

    @responses.activate
    def test_if_result_total_hits_zero_then_return_empty_list(self):
        result = create_response(
            records=[
                create_record_no_source()
            ]
        )
        self.assertEquals(
            result["hits"]["hits"], [{}]
        )
