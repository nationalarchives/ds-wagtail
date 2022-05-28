from django.test import TestCase
from django.urls import resolve


class TestiaidFromats(TestCase):
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
