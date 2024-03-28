import re

from django.test import SimpleTestCase

from etna.records.converters import IDConverter


class TestIDFormats(SimpleTestCase):
    def test_valid_formats(self):
        for label, value in (
            ("longformat", "3717ee38900740728076a61a398fcb84"),
            ("guid", "4d8dae2c-b417-4614-8ed8-924b9b4beeac"),
            ("dri_guid_plus", "00149557ca64456a8a41e44f14621801_1"),
            ("iaid_A", "A13530124"),
            ("iaid_C", "C2341693"),
            ("iaid_D", "D431198"),
            ("iaid_F", "F257629"),
            ("iaid_N", "N14562581"),
        ):
            id_regex = re.compile(IDConverter.regex)
            with self.subTest(label):
                self.assertTrue(id_regex.match(value))
