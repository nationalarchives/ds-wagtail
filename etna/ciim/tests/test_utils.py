from django.test import SimpleTestCase

from ..utils import pluck, find


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
