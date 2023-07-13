from django.test import SimpleTestCase, override_settings

from etna.records.models import Record
from etna.records.templatetags.records_tags import (
    is_page_current_item_in_hierarchy,
    level_name,
    record_url,
)


class TestRecordURLTag(SimpleTestCase):
    record_instance = Record(
        raw_data={
            "level": {
                "code": 2,
            },
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

    tna_record_instance = Record(
        raw_data={
            "@datatype": {
                "base": "aggregation",
                "group": [{"value": "aggregation"}, {"value": "tna"}],
            },
            "@hierarchy": [
                [
                    {
                        "@admin": {
                            "id": "C4",
                            "uuid": "9d7b9dbc-0bff-304f-98f1-8bdf2de76950",
                        },
                        "@entity": "reference",
                        "identifier": [
                            {
                                "primary": "true",
                                "reference_number": "ADM",
                                "type": "reference number",
                                "value": "ADM",
                            }
                        ],
                        "level": {"code": 1},
                        "source": {"value": "CAT"},
                        "summary": {
                            "title": "Records of the Admiralty, Naval Forces, Royal Marines, Coastguard, and related bodies"
                        },
                    },
                    {
                        "@admin": {
                            "id": "C714",
                            "uuid": "833d380a-1303-3fa1-ab16-a529d080150b",
                        },
                        "@entity": "reference",
                        "level": {"code": 2},
                        "source": {"value": "CAT"},
                        "summary": {"title": "Records of Naval Staff Departments"},
                    },
                    {
                        "@admin": {
                            "id": "C1931",
                            "uuid": "84e8175b-c6f7-3103-ad92-bfbc38e65668",
                        },
                        "@entity": "reference",
                        "identifier": [
                            {
                                "primary": "true",
                                "reference_number": "ADM 223",
                                "type": "reference number",
                                "value": "ADM 223",
                            }
                        ],
                        "level": {"code": 3},
                        "source": {"value": "CAT"},
                        "summary": {
                            "title": "Admiralty: Naval Intelligence Division and Operational Intelligence Centre: Intelligence..."
                        },
                    },
                ]
            ],
            "level": {
                "code": 3,
            },
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

    records_various = [
        (
            "ARCHON",
            Record(
                raw_data={
                    "source": {"value": "ARCHON"},
                    "@template": {
                        "details": {
                            "iaid": "A123456789",
                            "referenceNumber": "154",
                        }
                    },
                }
            ),
            "https://discovery.nationalarchives.gov.uk/details/a/A123456789",
        ),
        (
            "PROCAT",
            Record(
                raw_data={
                    "source": {"value": "CAT"},
                    "@template": {
                        "details": {
                            "iaid": "C12345678",
                            "referenceNumber": "AIR 79/1711/189046",
                        }
                    },
                }
            ),
            "https://discovery.nationalarchives.gov.uk/details/r/C12345678",
        ),
        (
            "ePRO",
            Record(
                raw_data={
                    "source": {"value": "CAT"},
                    "@template": {
                        "details": {
                            "iaid": "D1234567",
                            "referenceNumber": "WO 372/2/47705",
                        }
                    },
                }
            ),
            "https://discovery.nationalarchives.gov.uk/details/r/D1234567",
        ),
        (
            "CREATORS",
            Record(
                raw_data={
                    "@admin": {
                        "id": "F123456789",
                    },
                    "identifier": [
                        {
                            "faid": "F123456789",
                            "primary": True,
                            "type": "faid",
                            "value": "F123456789",
                        },
                    ],
                }
            ),
            "https://discovery.nationalarchives.gov.uk/details/c/F123456789",
        ),
        (
            "NRA",
            Record(
                raw_data={
                    "source": {"value": "NRA"},
                    "@template": {
                        "details": {
                            "iaid": "N13634630",
                        }
                    },
                },
            ),
            "https://discovery.nationalarchives.gov.uk/details/r/N13634630",
        ),
        (
            "MYC",
            Record(
                raw_data={
                    "source": {"value": "MYC"},
                    "@template": {
                        "details": {
                            "iaid": "efc75381-8a4c-4810-9e2f-340c3038ddc9",
                        }
                    },
                }
            ),
            "https://discovery.nationalarchives.gov.uk/details/r/efc75381-8a4c-4810-9e2f-340c3038ddc9",
        ),
        (
            "DRI",
            Record(
                raw_data={
                    "source": {"value": "CAT"},
                    "@template": {
                        "details": {
                            "iaid": "00149557ca64456a8a41e44f14621801_1",
                        }
                    },
                }
            ),
            "https://discovery.nationalarchives.gov.uk/details/r/00149557ca64456a8a41e44f14621801_1",
        ),
    ]

    def test_default(self):
        for attribute_name, expected_result in (
            ("record_instance", "/catalogue/ref/2515/300/1/"),
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
            ("record_instance", "/catalogue/ref/2515/300/1/"),
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

    def test_discovery_link_for_various_records(self):
        for iaid_format, record, expected_result in self.records_various:
            with self.subTest(iaid_format):
                self.assertEqual(
                    record_url(record, order_from_discovery=True), expected_result
                )

    def test_repository_links(self):
        for attribute_name, expected_result in (
            ("record_instance", "/catalogue/id/A13531109/"),
            ("record_instance_no_reference", ""),
        ):
            with self.subTest(attribute_name):
                source = getattr(self, attribute_name)
                self.assertEqual(record_url(source.repository), expected_result)

    def test_is_page_current_item_in_hierarchy(self):
        for current_record, expected_result in ((self.record_instance, True),):
            with self.subTest(current_record):
                # We pass in the "current" record and this then
                # checks if the current record is in the hierarchy
                self.assertEqual(
                    is_page_current_item_in_hierarchy(current_record, current_record),
                    expected_result,
                )

    def test_level_name(self):
        for current_record, expected_result in (
            (self.tna_record_instance, "Series"),
            (self.record_instance, "Sub-fonds"),
        ):
            with self.subTest(self):
                # We pass in the current record level code and is_tna value
                # and this function then retrieves the level name associated
                # with that level code/record
                self.assertEqual(
                    level_name(current_record.level_code, current_record.is_tna),
                    expected_result,
                )
