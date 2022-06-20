from django.test import SimpleTestCase

from ..utils import (
    convert_sort_key_to_index,
    find,
    find_all,
    format_description_markup,
    pluck,
)


class TestResolveLinks(SimpleTestCase):
    def test_test(self):
        markup = (
            '<span><span class="extref" link="$link(C11996672)">link text</span></span>'
        )

        stripped_markup = format_description_markup(markup)

        self.assertEquals(
            '<span><a href="/catalogue/id/C11996672/">link text</a></span>',
            stripped_markup,
        )

    def test_no_links(self):
        markup = "<span></span>"

        stripped_markup = format_description_markup(markup)

        self.assertEquals("<span/>", stripped_markup)

    def test_multiple_links(self):
        markup = (
            "<span>"
            '<span class="extref" link="$link(C11996672)">link text one</span>'
            '<span class="extref" link="$link(C11996673)">link text two</span>'
            "</span>"
        )

        stripped_markup = format_description_markup(markup)

        self.assertEquals(
            (
                "<span>"
                '<a href="/catalogue/id/C11996672/">link text one</a>'
                '<a href="/catalogue/id/C11996673/">link text two</a>'
                "</span>"
            ),
            stripped_markup,
        )

    def test_external_link(self):
        markup = (
            "<span>"
            '<span class="extref" href="http://example.com/">link text one</span>'
            "</span>"
        )

        stripped_markup = format_description_markup(markup)

        self.assertEquals(
            ("<span>" '<a href="http://example.com/">link text one</a>' "</span>"),
            stripped_markup,
        )

    def test_invalid_link(self):
        # C3829405 contains an span.extref with no href
        markup = "<span>" '<span class="extref">Invalid link</span>' "</span>"

        stripped_markup = format_description_markup(markup)

        self.assertEquals(
            ("<span></span>"),
            stripped_markup,
        )


class TestPluck(SimpleTestCase):
    def test_pluck_from_dict_in_list(self):
        items = [{"name": "Jupiter"}, {"name": "Saturn"}]

        result = pluck(items, accessor=lambda i: i["name"])

        self.assertEqual(result, "Jupiter")

    def test_pluck_from_list(self):
        items = [["Jupiter"], ["Saturn"]]

        result = pluck(items, accessor=lambda i: i[0])

        self.assertEqual(result, "Jupiter")

    def test_pluck_with_no_accessor(self):
        items = [["Jupiter"], ["Saturn"]]

        result = pluck(items)

        self.assertEqual(result, None)

    def test_pluck_with_default(self):
        items = None

        result = pluck(items, default="Default")

        self.assertEqual(result, "Default")

    def test_pluck_type_error_returns_default(self):
        items = None

        result = pluck(items, accessor=lambda i: i[0], default="Default")

        self.assertEqual(result, "Default")

    def test_key_error_returns_default(self):
        items = None

        result = pluck(items, lambda i: i["invalid_key"], default="Default")

        self.assertEqual(result, "Default")

    def test_index_error_returns_default(self):
        items = None

        result = pluck(items, lambda i: i[10], default="Default")

        self.assertEqual(result, "Default")


class TestFind(SimpleTestCase):
    def test_find_from_dict_in_list(self):
        items = [{"name": "Jupiter"}, {"name": "Saturn"}]

        result = find(items, predicate=lambda i: i["name"])

        self.assertEqual(result, {"name": "Jupiter"})

    def test_find_from_list(self):
        items = [["Jupiter"], ["Saturn"]]

        result = find(items, predicate=lambda i: i[0])

        self.assertEqual(result, ["Jupiter"])

    def test_find_with_no_predicate(self):
        items = [["Jupiter"], ["Saturn"]]

        result = find(items)

        self.assertEqual(result, None)

    def test_find_type_error_returns_none(self):
        items = None

        result = find(items, predicate=lambda i: i[0])

        self.assertEqual(result, None)

    def test_key_error_returns_none(self):
        items = None

        result = find(items, lambda i: i["invalid_key"])

        self.assertEqual(result, None)

    def test_index_error_returns_none(self):
        items = None

        result = find(items, lambda i: i[10])

        self.assertEqual(result, None)


class TestFindAll(SimpleTestCase):
    def test_find_from_dict_in_list(self):
        items = [
            {"name": "Mercury", "moon_count": 0},
            {"name": "Jupiter", "moon_count": 79},
            {"name": "Saturn", "moon_count": 82},
        ]

        result = find_all(items, predicate=lambda i: i["moon_count"] > 1)

        self.assertEqual(
            list(result),
            [
                {"name": "Jupiter", "moon_count": 79},
                {"name": "Saturn", "moon_count": 82},
            ],
        )

    def test_find_from_list(self):
        items = [["Jupiter"], ["Saturn"]]

        result = find_all(items, predicate=lambda i: i[0].startswith("J"))

        self.assertEqual(list(result), [["Jupiter"]])

    def test_find_with_no_predicate(self):
        items = [["Jupiter"], ["Saturn"]]

        result = find_all(items)

        self.assertEqual(list(result), [])

    def test_find_type_error_returns_empty_list(self):
        items = None

        result = find_all(items, predicate=lambda i: i[0])

        self.assertEqual(list(result), [])

    def test_key_error_returns_empty_list(self):
        items = None

        result = find_all(items, lambda i: i["invalid_key"])

        self.assertEqual(list(result), [])

    def test_index_error_returns_empty_list(self):
        items = None

        result = find_all(items, lambda i: i[10])

        self.assertEqual(list(result), [])


class TestConvertSortKeyToIndex(SimpleTestCase):
    def test_none(self):
        sort = None

        index = convert_sort_key_to_index(sort)

        self.assertEquals(index, 0)

    def test_empty_string(self):
        sort = None

        index = convert_sort_key_to_index(sort)

        self.assertEquals(index, 0)

    def test_converts_sort_key_with_leading_zero(self):
        sort = "01"

        index = convert_sort_key_to_index(sort)

        self.assertEquals(index, 0)

    def test_converts_sort_key_at_three_digit_boundary(self):
        sort = "31000"

        index = convert_sort_key_to_index(sort)

        self.assertEquals(index, 999)

    def test_converts_sort_key_at_four_digit_boundary(self):
        sort = "31001"

        index = convert_sort_key_to_index(sort)

        self.assertEquals(index, 1000)

    def test_index_is_zero_for_invalid_sort_key(self):
        sort = "10000"

        index = convert_sort_key_to_index(sort)

        self.assertEquals(index, 0)

    def test_index_is_zero_for_non_int_sort_key(self):
        sort = "NaN"

        index = convert_sort_key_to_index(sort)

        self.assertEquals(index, 0)
