from django.test import SimpleTestCase

from ..utils import format_description_markup, pluck, find


# http://adb64ece119d042fcaaa54b1ddcdd687-df4cb78551b008e8.elb.eu-west-2.amazonaws.com/search?term=C11996678
class TestResolveLinks(SimpleTestCase):
    def test_test(self):
        markup = (
            '<span><span class="extref" link="$link(C11996672)">link text</span></span>'
        )

        stripped_markup = format_description_markup(markup)

        self.assertEquals(
            '<span><a href="/catalogue/C11996672/">link text</a></span>',
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
                '<a href="/catalogue/C11996672/">link text one</a>'
                '<a href="/catalogue/C11996673/">link text two</a>'
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
            (
                "<span>"
                '<a href="http://example.com/">link text one</a>'
                "</span>"
            ),
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
