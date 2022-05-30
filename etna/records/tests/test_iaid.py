from django.test import TestCase
from django.urls import resolve


class TestIaidFormats(TestCase):
    def test_iaid_long_mixed_format(self):
        longformat = "3717ee38900740728076a61a398fcb84"
        resolver = resolve("/catalogue/id/" + longformat + "/")
        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], longformat)

    def test_iaid_guid_format(self):
        guid = "4d8dae2c-b417-4614-8ed8-924b9b4beeac"
        resolver = resolve("/catalogue/id/" + guid + "/")
        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], guid)

    def test_iaid_A13530124_format(self):
        iaid = "A13530124"
        resolver = resolve("/catalogue/id/" + iaid + "/")
        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], iaid)

    def test_iaid_C2341693_format(self):
        iaid = "C2341693"
        resolver = resolve("/catalogue/id/" + iaid + "/")
        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], iaid)

    def test_iaid_D431198_format(self):
        iaid = "D431198"
        resolver = resolve("/catalogue/id/" + iaid + "/")
        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], iaid)

    def test_iaid_F257629_format(self):
        iaid = "F257629"
        resolver = resolve("/catalogue/id/" + iaid + "/")
        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], iaid)

    def test_iaid_N14562581_format(self):
        iaid = "N14562581"
        resolver = resolve("/catalogue/id/" + iaid + "/")
        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], iaid)
