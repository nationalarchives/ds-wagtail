from django.test import SimpleTestCase, override_settings

from etna.records.models import Record
from etna.records.templatetags.records_tags import record_url


class TestRecordURLTag(SimpleTestCase):

    # A sample search result respresentation, as encountered in search views
    # (where no up-front transformation is applied)
    record_search_hit = {
        "_score": 1,
        "_source": {
            "@template": {
                "details": {
                    "iaid": "e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
                    "referenceNumber": "2515/300/1",
                    "summaryTitle": "Test",
                }
            }
        },
    }

    # A sample search result respresentation, as encountered in search views
    # (where no up-front transformation is applied)
    interpretive_search_hit = {
        "_score": 1,
        "_source": {
            "@template": {
                "details": {
                    "sourceUrl": "https://www.example.com",
                    "primaryIdentifier": "bp-2304",
                    "summaryTitle": "Test",
                }
            }
        },
    }

    # A sample item representation, as returned by Record.related_records
    partial_record_dict = {
        "iaid": "e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
        "reference_number": "2515/300/1",
        "title": "Test",
    }

    # A sample item representation, as returned by Record.related_articles
    partial_interpretive_dict = {
        "url": "http://www.example.com",
        "title": "Test",
    }

    # A sample Record representation, as encountered in record detail views
    # (where values are prepared up-front by transform_record_result())
    record_instance = Record(
        iaid="e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
        reference_number="2515/300/1",
        title="Test",
    )

    # A sample Record representation, as encountered in record detail views
    # (where values are prepared up-front by transform_record_result())
    record_instance_no_reference = Record(
        iaid="e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
        reference_number=None,
        title="Test",
    )

    def test_default(self):
        for attribute_name, expected_result in (
            (
                "record_search_hit",
                "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/",
            ),
            ("interpretive_search_hit", "https://www.example.com"),
            (
                "partial_record_dict",
                "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/",
            ),
            ("partial_interpretive_dict", ""),
            ("record_instance", "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/"),
            (
                "record_instance_no_reference",
                "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/",
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
                "record_search_hit",
                "https://discovery.nationalarchives.gov.uk/details/r/e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
            ),
            ("interpretive_search_hit", "https://www.example.com"),
            (
                "partial_record_dict",
                "https://discovery.nationalarchives.gov.uk/details/r/e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
            ),
            ("partial_interpretive_dict", ""),
            (
                "record_instance",
                "https://discovery.nationalarchives.gov.uk/details/r/e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
            ),
            (
                "record_instance_no_reference",
                "https://discovery.nationalarchives.gov.uk/details/r/e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
            ),
        ):
            with self.subTest(attribute_name):
                source = getattr(self, attribute_name)
                self.assertEqual(record_url(source, is_editorial=True), expected_result)

    @override_settings(FEATURE_RECORD_LINKS_GO_TO_DISCOVERY=True)
    def test_no_discovery_links_when_is_editorial_is_false(self):
        for attribute_name, expected_result in (
            (
                "record_search_hit",
                "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/",
            ),
            ("interpretive_search_hit", "https://www.example.com"),
            (
                "partial_record_dict",
                "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/",
            ),
            ("partial_interpretive_dict", ""),
            ("record_instance", "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/"),
            (
                "record_instance_no_reference",
                "/catalogue/id/e7e92a0b-3666-4fd6-9dac-9d9530b0888c/",
            ),
        ):
            with self.subTest(attribute_name):
                source = getattr(self, attribute_name)
                self.assertEqual(
                    record_url(source, is_editorial=False), expected_result
                )
