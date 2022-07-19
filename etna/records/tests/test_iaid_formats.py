import re

from django.test import SimpleTestCase

from etna.records.converters import metadataIdConverter


class TestmetadataIdFormats(SimpleTestCase):
    def test_valid_formats(self):
        for label, value in (
            ("longformat", "3717ee38900740728076a61a398fcb84"),
            ("guid", "4d8dae2c-b417-4614-8ed8-924b9b4beeac"),
            ("dri_guid_plus", "00149557ca64456a8a41e44f14621801_1"),
            ("metadataId_A", "A13530124"),
            ("metadataId_C", "C2341693"),
            ("metadataId_D", "D431198"),
            ("metadataId_F", "F257629"),
            ("metadataId_N", "N14562581"),
        ):
            metadataId_regex = re.compile(metadataIdConverter.regex)
            with self.subTest(label):
                self.assertTrue(metadataId_regex.match(value))
