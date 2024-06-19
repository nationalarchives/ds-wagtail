from datetime import date

from django.test import SimpleTestCase

from ..utils import (
    ValueExtractionError,
    convert_sort_key_to_index,
    extract,
    find,
    find_all,
    format_description_markup,
    pluck,
    prepare_ohos_params,
    strip_html,
)


class InnerTypeError(TypeError):
    pass


TODAY = date.today()


class TestExtract(SimpleTestCase):
    test_data = {
        "item": {
            "id": 2,
            "name": "foo",
            "date_created": TODAY,
            "parent": {
                "id": 1,
                "name": "parent",
                "date_created": TODAY,
            },
            "children": [
                {"id": 3, "name": "bar", "date_created": TODAY},
                {"id": 4, "name": "baz", "date_created": TODAY},
            ],
        }
    }

    def test_successes(self):
        """
        Show that we can extract values via:
        - dict keys
        - sequence indexes
        - object attribute names
        """
        for key, expected_value in (
            ("item", self.test_data["item"]),
            ("item.id", 2),
            ("item.date_created", TODAY),
            ("item.date_created.day", TODAY.day),
            ("item.parent.id", 1),
            ("item.parent.date_created.year", TODAY.year),
            ("item.children.0.id", 3),
            ("item.children.0.date_created.month", TODAY.month),
            ("item.children.1.id", 4),
            ("item.children.1.date_created.month", TODAY.month),
        ):
            with self.subTest(key):
                self.assertEqual(
                    extract(self.test_data, key),
                    expected_value,
                )

    def test_without_defaults(self):
        """
        Shows that wherever in the process the failure happens, it is
        reported as a ValueExtractionError with a useful description.
        """
        for key, problematic_bit, error_class in (
            ("item_2", "item_2", KeyError),
            ("item.invalid_key", "invalid_key", KeyError),
            ("item.date_created.invalid_attr", "invalid_attr", AttributeError),
            ("item.children.invalid_index", "invalid_index", AttributeError),
            ("item.children.999", "999", IndexError),
            ("item.children.1.invalid_key", "invalid_key", KeyError),
            (
                "item.children.1.date_created.invalid_attr",
                "invalid_attr",
                AttributeError,
            ),
        ):
            with self.subTest(key):
                msg_part = f"{error_class} raised when extracting '{problematic_bit}'"
                with self.assertRaisesRegex(ValueExtractionError, msg_part):
                    extract(self.test_data, key)

    def test_with_defaults(self):
        """
        Shows that wherever in the process the failure happens, no exception
        is raised, and the default value is returned.
        """
        for key, default_value in (
            ("item_2", "somestring"),
            ("item.invalid_key", 1),
            ("item.date_created.invalid_attr", None),
            ("item.children.invalid_index", TODAY),
            ("item.children.999", None),
            ("item.children.1.invalid_key", False),
            ("item.children.1.date_created.invalid_attr", True),
        ):
            with self.subTest(key):
                self.assertIs(
                    extract(self.test_data, key, default=default_value), default_value
                )


class TestResolveLinks(SimpleTestCase):
    def test_test(self):
        markup = (
            '<span><span class="extref" link="$link(C11996672)">link text</span></span>'
        )

        stripped_markup = format_description_markup(markup)

        self.assertEqual(
            '<span><a href="/catalogue/id/C11996672/">link text</a></span>',
            stripped_markup,
        )

    def test_no_links(self):
        markup = "<span></span>"

        stripped_markup = format_description_markup(markup)

        self.assertEqual("<span/>", stripped_markup)

    def test_multiple_links(self):
        markup = (
            "<span>"
            '<span class="extref" link="$link(C11996672)">link text one</span>'
            '<span class="extref" link="$link(C11996673)">link text two</span>'
            "</span>"
        )

        stripped_markup = format_description_markup(markup)

        self.assertEqual(
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

        self.assertEqual(
            ("<span>" '<a href="http://example.com/">link text one</a>' "</span>"),
            stripped_markup,
        )

    def test_invalid_link(self):
        # C3829405 contains an span.extref with no href
        markup = "<span>" '<span class="extref">Invalid link</span>' "</span>"

        stripped_markup = format_description_markup(markup)

        self.assertEqual(
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

        self.assertEqual(index, 0)

    def test_empty_string(self):
        sort = None

        index = convert_sort_key_to_index(sort)

        self.assertEqual(index, 0)

    def test_converts_sort_key_with_leading_zero(self):
        sort = "01"

        index = convert_sort_key_to_index(sort)

        self.assertEqual(index, 0)

    def test_converts_sort_key_at_three_digit_boundary(self):
        sort = "31000"

        index = convert_sort_key_to_index(sort)

        self.assertEqual(index, 999)

    def test_converts_sort_key_at_four_digit_boundary(self):
        sort = "31001"

        index = convert_sort_key_to_index(sort)

        self.assertEqual(index, 1000)

    def test_index_is_zero_for_invalid_sort_key(self):
        sort = "10000"

        index = convert_sort_key_to_index(sort)

        self.assertEqual(index, 0)

    def test_index_is_zero_for_non_int_sort_key(self):
        sort = "NaN"

        index = convert_sort_key_to_index(sort)

        self.assertEqual(index, 0)


class TestStripHtml(SimpleTestCase):

    def test_ensure_spaces_preserve_marks(self):

        test_data = (
            (
                "test for span tag",
                "This is a<span>test example</span>",
                "This is a test example",
            ),
            (
                "test for p tag",
                "This is a<p>test example</p>",
                "This is a test example",
            ),
            (
                "test for unknown tag",
                "This is a<unknown>test example</unknown>",
                "This is atest example",
            ),
            (
                "D7376859",
                '<span class="wrapper"><span altrender="doctype" class="emph"></span><span class="persname"><span altrender="surname" class="emph">Patman</span><span altrender="forenames" class="emph">Clifford Douglas</span></span><span altrender="rank" class="emph">Armament Quarter Master Serjeant</span><span altrender="regno" class="emph">1865334</span><span class="corpname">Royal Army Ordnance Corps, 8 Hussars now Royal Electrical and Mechanical Engineers</span><span class="geogname">Escape and Evasion</span><span altrender="award" class="emph">Mentions in Despatches</span></span>',
                "Patman Clifford Douglas Armament Quarter Master Serjeant 1865334 Royal Army Ordnance Corps, 8 Hussars now Royal Electrical and Mechanical Engineers Escape and Evasion Mentions in Despatches",
            ),
        )

        for label, value, expected in test_data:
            with self.subTest(label):
                result = strip_html(value, preserve_marks=True, ensure_spaces=True)
                self.assertEqual(result, expected)

    def test_allow_tags(self):
        value = """<a href="http://test.com">this is a test</a>"""
        expected = (
            """<a href="http://test.com" rel="noopener noreferrer">this is a test</a>"""
        )
        allow_tags = {"a", "br", "p"}
        result = strip_html(value, allow_tags=allow_tags)
        self.assertEqual(result, expected)


class TestPrepareOhosParam(SimpleTestCase):

    def test_prepare_ohos_param(self):

        test_data = (
            (
                "orphan selection",
                (
                    ["community"],
                    ["collection:Sharing Wycombe's Old Photographs", "group:community"],
                ),
                (
                    ["community"],
                    [
                        "collectionOhos:Sharing Wycombe's Old Photographs",
                        "group:community",
                    ],
                ),
            ),
            (
                "parent selection",
                (
                    ["community"],
                    [
                        "collection:parent-collectionSurrey:Surrey History Centre",
                        "collection:parent-collectionMorrab:Morrab Photo Archive",
                        "group:community",
                    ],
                ),
                (
                    ["community", "collectionSurrey", "collectionMorrab"],
                    [
                        "collectionOhos:Surrey History Centre",
                        "collectionOhos:Morrab Photo Archive",
                        "group:community",
                    ],
                ),
            ),
            (
                "parent children selection",
                (
                    ["community"],
                    [
                        "collection:parent-collectionSurrey:Surrey History Centre",
                        "collection:child-collectionSurrey:GYPSY ROMA TRAVELLER HISTORY MONTH: RECORDED INTERVIEWS",
                        "collection:child-collectionSurrey:LINGFIELD ORAL HISTORY PROJECT: TRANSCRIPTS",
                        "collection:parent-collectionMorrab:Morrab Photo Archive",
                        "collection:child-collectionMorrab:Miscellaneous Photos",
                        "group:community",
                    ],
                ),
                (
                    ["community", "collectionSurrey", "collectionMorrab"],
                    [
                        "collectionOhos:GYPSY ROMA TRAVELLER HISTORY MONTH: RECORDED INTERVIEWS",
                        "collectionOhos:LINGFIELD ORAL HISTORY PROJECT: TRANSCRIPTS",
                        "collectionOhos:Miscellaneous Photos",
                        "group:community",
                    ],
                ),
            ),
            (
                "children selection",
                (
                    ["community"],
                    [
                        "collection:child-collectionSurrey:GYPSY ROMA TRAVELLER HISTORY MONTH: RECORDED INTERVIEWS",
                        "collection:child-collectionSurrey:LINGFIELD ORAL HISTORY PROJECT: TRANSCRIPTS",
                        "collection:child-collectionMorrab:Miscellaneous Photos",
                        "group:community",
                    ],
                ),
                (
                    ["community", "collectionSurrey", "collectionMorrab"],
                    [
                        "collectionOhos:GYPSY ROMA TRAVELLER HISTORY MONTH: RECORDED INTERVIEWS",
                        "collectionOhos:LINGFIELD ORAL HISTORY PROJECT: TRANSCRIPTS",
                        "collectionOhos:Miscellaneous Photos",
                        "group:community",
                    ],
                ),
            ),
        )

        for label, value, expected in test_data:
            with self.subTest(label):
                aggs, filter = prepare_ohos_params(*value)
                aggs_equality = set(aggs).issubset(set(expected[0]))
                filter_equality = set(filter).issubset(set(expected[1]))
                self.assertTrue(aggs_equality)
                self.assertTrue(filter_equality)
