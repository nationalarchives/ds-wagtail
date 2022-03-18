from django.test import RequestFactory, SimpleTestCase

from ..templatetags.search_tags import (
    get_selected_filters,
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


class GetSelectedFiltersTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_no_selected_filters_returns_empty_dict(self):
        context = {"request": self.factory.get("?test=true&to-remove=1")}

        selected_filters = get_selected_filters(context)

        self.assertEqual(selected_filters, {})

    def test_selected_collection(self):
        context = {"request": self.factory.get("?collections=collection:MAF")}

        selected_filters = get_selected_filters(context)

        self.assertEqual(
            selected_filters,
            {
                "collections": ["collection:MAF"],
            },
        )

    def test_multiple_selected_filters_with_same_param(self):
        context = {
            "request": self.factory.get(
                "?collections=collection:MAF&collections=collection:WO"
            )
        }

        selected_filters = get_selected_filters(context)

        self.assertEqual(
            selected_filters,
            {
                "collections": ["collection:MAF", "collection:WO"],
            },
        )
