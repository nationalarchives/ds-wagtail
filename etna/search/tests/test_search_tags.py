from datetime import date
from unittest import mock

from django.forms.boundfield import BoundField
from django.test import RequestFactory, SimpleTestCase
from django.utils.datastructures import MultiValueDict

from etna.ciim.constants import BucketKeys

from ..forms import CatalogueSearchForm
from ..templatetags.search_tags import (
    extended_in_operator,
    query_string_exclude,
    query_string_include,
    render_fields_as_hidden,
    render_sort_input,
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


class RenderFieldsAsHiddenTest(SimpleTestCase):
    def setUp(self):
        self.form = CatalogueSearchForm(
            data=MultiValueDict(
                {
                    "q": "test",
                    "group": "tna",
                    "sort": "relevance",
                    "opening_start_date_0": "01",
                    "opening_start_date_1": "01",
                    "opening_start_date_2": "2000",
                    "collection": ["ADM", "AIR", "WO"],
                }
            )
        )

    @mock.patch(
        "etna.search.templatetags.search_tags.get_random_string", return_value="123"
    )
    @mock.patch.object(BoundField, "as_hidden", return_value="", autospec=True)
    def test_generates_random_suffixes_for_input_ids(
        self, mocked_as_hidden, mocked_get_random_string
    ):
        render_fields_as_hidden(self.form, include="q")
        mocked_as_hidden.assert_called_once_with(
            self.form["q"], attrs={"id": "id_q_123"}
        )

    @mock.patch.object(BoundField, "as_hidden", return_value="", autospec=True)
    def test_exclude(self, mocked_as_hidden):
        exclude_names = ("q", "group", "sort")

        # call the function under test
        render_fields_as_hidden(self.form, exclude=" ".join(exclude_names))

        # assert as_hidden() was called for the correct fields
        for field in self.form:
            if field.name in exclude_names:
                with self.subTest(
                    f"as_hidden() should NOT have been called for field: '{field.name}'"
                ):
                    with self.assertRaises(AssertionError):
                        mocked_as_hidden.assert_any_call(field, attrs=mock.ANY)
            else:
                with self.subTest(
                    f"as_hidden() should have been called for field: '{field.name}'"
                ):
                    mocked_as_hidden.assert_any_call(field, attrs=mock.ANY)

    @mock.patch.object(BoundField, "as_hidden", return_value="", autospec=True)
    def test_include(self, mocked_as_hidden):
        include_names = ("q", "group")

        # call the function under test
        render_fields_as_hidden(self.form, include=" ".join(include_names))

        # assert as_hidden() was called for the correct fields
        for field in self.form:
            if field.name not in include_names:
                with self.subTest(
                    f"as_hidden() should NOT have been called for field: '{field.name}'"
                ):
                    with self.assertRaises(AssertionError):
                        mocked_as_hidden.assert_any_call(field, attrs=mock.ANY)
            else:
                with self.subTest(
                    f"as_hidden() should have been called for field: '{field.name}'"
                ):
                    mocked_as_hidden.assert_any_call(field, attrs=mock.ANY)


class RenderSortTest(SimpleTestCase):
    def setUp(self):
        self.form = CatalogueSearchForm(
            {
                "group": BucketKeys.COMMUNITY,
                "sort": "relevance",
            }
        )

    def test_render_sort_input_input_id(self):
        expected_html = '<select name="sort" class="search-sort-view__form-select" id="id_sort_somevalue" aria-invalid="true">'
        self.assertIn(
            expected_html, render_sort_input(self.form, id_suffix="somevalue")
        )
