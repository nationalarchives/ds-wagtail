from django.test import SimpleTestCase
import responses
from ..transforms import transform_record_result
from ...ciim.exceptions import InValidResult

from ...ciim.tests.factories import *

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
    def test_if_result_total_hit_value_morethanzero_and_no_source_rais_invalid_result(self):
        result = create_response(
            records=[
                create_record_no_source()
            ]
        )
        with self.assertRaises(InValidResult):
            transform_record_result(result)

    @responses.activate
    def test_if_result_total_hit_value_zero_must_return_empty(self):
        result = create_response(
            records=[]
        )
        self.assertEquals(
            transform_record_result(result), {}
        )
