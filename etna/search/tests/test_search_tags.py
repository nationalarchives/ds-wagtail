from datetime import date

from django.test import RequestFactory, SimpleTestCase

from ..templatetags.search_tags import (
    extended_in_operator,
    query_string_exclude,
    query_string_include,
)


class QueryStringTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_add_new_parameter(self):
        context = {"request": self.factory.get("?test=true")}
        result = query_string_include(context, "page", "1")

        self.assertEqual(result, "test=true&page=1")

    def test_update_existing_parameter(self):
        context = {"request": self.factory.get("?page=1")}
        result = query_string_include(context, "page", "2")

        self.assertEqual(result, "page=2")


class QueryStringExcludeTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_remove_parameter(self):
        context = {"request": self.factory.get("?test=true&to-remove=1")}
        result = query_string_exclude(context, "to-remove", "1")

        self.assertEqual(result, "test=true")

    def test_ensure_values_are_cast_to_strings(self):
        # All params in QueryDict are strings, values passed to tag should be
        # cast during comparison.
        context = {"request": self.factory.get("?test=true&page=1")}
        result = query_string_exclude(context, "page", 1)

        self.assertEqual(result, "test=true")

    def test_ensure_correct_param_is_removed_if_multiple_exist(self):
        # All params in QueryDict are strings, values passed to tag should be
        # cast during comparison.
        context = {"request": self.factory.get("?param=to-remove&param=to-keep")}
        result = query_string_exclude(context, "param", "to-remove")

        self.assertEqual(result, "param=to-keep")

    def test_matching_parameter_with_different_value_is_not_removed(self):
        context = {"request": self.factory.get("?test=true&page=1")}
        result = query_string_exclude(context, "page", "2")

        self.assertEqual(result, "test=true&page=1")

    def test_non_existant_parameter(self):
        context = {"request": self.factory.get("?test=true")}
        result = query_string_exclude(context, "page", "1")

        self.assertEqual(result, "test=true")

    def test_record_opening_year_lessthan_four_digits(self):
        context = {
            "request": self.factory.get(
                "?opening_start_date_0=&opening_start_date_1=&opening_start_date_2=19&opening_end_date_0=&opening_end_date_1=&opening_end_date_2=200"
            )
        }

        for field_name, value, expected_result in (
            (
                "opening_start_date",
                date(19, 1, 1),
                "opening_end_date_0=&opening_end_date_1=&opening_end_date_2=200",
            ),
            (
                "opening_end_date",
                date(200, 1, 1),
                "opening_start_date_0=&opening_start_date_1=&opening_start_date_2=19",
            ),
        ):
            with self.subTest(field_name):
                result = query_string_exclude(context, field_name, value)
                self.assertEqual(result, expected_result)


class TestExtendedInOperator(SimpleTestCase):
    def test_extended_in_operator(self):
        for label, value, expected in (
            (
                "test_match_notfound",
                ("a", "b", "c"),
                False,
            ),
            (
                "test_match_found",
                ("c", "b", "c"),
                True,
            ),
            (
                "test_none_found",
                (None, "b", None),
                True,
            ),
            (
                "test_none_not_found",
                (None, "b", "c"),
                False,
            ),
        ):
            with self.subTest(label):
                result = extended_in_operator(value[0], value[1], value[2])
                self.assertEqual(result, expected)
