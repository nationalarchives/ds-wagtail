from django.test import SimpleTestCase, override_settings

from etna.records.models import Record
from etna.records.templatetags.records_tags import record_url


class TestRecordURLTag(SimpleTestCase):
    record_instance = Record(
        raw_data={
            "repository": {
                "@admin": {
                    "id": "A13531109",
                }
            },
            "@template": {
                "details": {
                    "iaid": "e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
                    "referenceNumber": "2515/300/1",
                    "summaryTitle": "Test",
                }
            },
        }
    )

    record_instance_no_reference = Record(
        raw_data={
            "@template": {
                "details": {
                    "iaid": "e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
                    "summaryTitle": "Test",
                }
            }
        }
    )

    interpretive_record = Record(
        raw_data={
            "@template": {
                "details": {
                    "iaid": "ip-3162",
                    "summaryTitle": "Insights page",
                    "sourceUrl": "https://www.example.com",
                }
            }
        }
    )

    def test_default(self):
        for attribute_name, expected_result in (
            ("record_instance", "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/"),
            (
                "record_instance_no_reference",
                "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/",
            ),
            (
                "interpretive_record",
                "https://www.example.com",
            ),
        ):
            with self.subTest(attribute_name):
                source = getattr(self, attribute_name)

                self.assertEqual(
                    record_url(source, is_editorial=False), expected_result
                )
                # is_editorial should't make a difference unless
                # FEATURE_RECORD_LINKS_GO_TO_DISCOVERY is True
                self.assertEqual(record_url(source, is_editorial=True), expected_result)

    @override_settings(FEATURE_RECORD_LINKS_GO_TO_DISCOVERY=True)
    def test_discovery_links_when_is_editorial_is_true(self):
        for attribute_name, expected_result in (
            (
                "record_instance",
                "https://discovery.nationalarchives.gov.uk/details/r/e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
            ),
            (
                "record_instance_no_reference",
                "https://discovery.nationalarchives.gov.uk/details/r/e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
            ),
            (
                "interpretive_record",
                "https://www.example.com",
            ),
        ):
            with self.subTest(attribute_name):
                source = getattr(self, attribute_name)
                self.assertEqual(record_url(source, is_editorial=True), expected_result)

    @override_settings(FEATURE_RECORD_LINKS_GO_TO_DISCOVERY=True)
    def test_no_discovery_links_when_is_editorial_is_false(self):
        for attribute_name, expected_result in (
            ("record_instance", "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/"),
            (
                "record_instance_no_reference",
                "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/",
            ),
            (
                "interpretive_record",
                "https://www.example.com",
            ),
        ):
            with self.subTest(attribute_name):
                source = getattr(self, attribute_name)
                self.assertEqual(
                    record_url(source, is_editorial=False), expected_result
                )

    def test_repository_links(self):
        for attribute_name, expected_result in (
            ("record_instance", "/catalogue/id/A13531109/"),
            ("record_instance_no_reference", ""),
        ):
            with self.subTest(attribute_name):
                source = getattr(self, attribute_name)
                self.assertEqual(record_url(source.repository), expected_result)
