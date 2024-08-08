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
            ("ohos-media", "media-wmk-20485"),
            ("ohos-osc", "osc-16758"),
            ("ohos-pcw", "pcw-41083"),
            ("ohos-pcw-2", "pcw-438573.0"),
            ("ohos-swop", "swop-49209"),
            ("ohos-wmk", "wmk-16758"),
            ("ohos-shc-1", "shc-7694-6-1-1-4"),
            ("ohos-shc-2", "shc-CC1174-2-1-1-1"),
            ("ohos-mpa", "mpa-12345"),
            ("ohos-sid", "sid-12345"),
        ):
            id_regex = re.compile(IDConverter.regex)
            with self.subTest(label):
                self.assertTrue(id_regex.fullmatch(value))
