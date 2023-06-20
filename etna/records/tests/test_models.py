import json
import unittest

from copy import deepcopy

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

import responses

from ...ciim.tests.factories import create_media, create_record, create_response
from ...ciim.utils import ValueExtractionError
from ..api import get_records_client
from ..models import Image, Record


class RecordModelTests(SimpleTestCase):
    fixture_path = f"{settings.BASE_DIR}/etna/ciim/tests/fixtures/record.json"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.records_client = get_records_client()
        with open(cls.fixture_path, "r") as f:
            cls.fixture_contents = json.loads(f.read())

    def setUp(self):
        self.record = Record(deepcopy(self.fixture_contents["hits"]["hits"][0]))

    def test_template_uses_detail_template_when_present(self):
        self.assertIn("details", self.record._raw["@template"])
        self.assertEqual(self.record.template, self.record._raw["@template"]["details"])

    def test_template_uses_results_template_if_details_template_not_present(self):
        self.assertIn("results", self.record._raw["@template"])

        # patch raw data
        self.record._raw["@template"].pop("details")

        self.assertEqual(self.record.template, self.record._raw["@template"]["results"])

    def test_template_returns_empty_dict_when_no_template_available(self):
        # patch raw data
        self.record._raw["@template"] = {}
        self.assertEqual(self.record.template, {})

    def test_iaid(self):
        self.assertEqual(self.record.iaid, "C10297")

    def test_returns_blank_string_when_data_not_present(self):
        # patch raw data
        self.record._raw["@admin"].pop("id")
        self.record._raw["@template"]["details"].pop("iaid")
        self.assertEqual(self.record.iaid, "")

    def test_returns_blank_string_when_iaid_value_is_invalid(self):
        # patch raw data
        invalid_value = "bp-299"
        self.record._raw["@admin"]["id"] = invalid_value
        self.record._raw["@template"]["details"]["iaid"] = invalid_value
        self.assertEqual(self.record.iaid, "")

    def test_summary_title(self):
        self.assertEqual(
            self.record.summary_title,
            "Law Officers' Department: Registered Files",
        )

    def test_reference_number(self):
        self.assertEqual(self.record.reference_number, "LO 2")

    def test_raises_valueextractionerror_when_reference_number_is_not_present(self):
        # patch raw data
        self.record._raw.pop("identifier")
        self.record._raw["@template"]["details"].pop("referenceNumber")

        self.assertEqual(self.record.reference_number, "")

    def test_source_url(self):
        # patch raw data
        url = "http://dummy.com"
        self.record._raw["@template"]["details"]["sourceUrl"] = url

        self.assertTrue(self.record.has_source_url())
        self.assertEqual(self.record.source_url, url)

    def test_raises_valueextractionerror_if_url_not_present(self):
        self.assertFalse(self.record.has_source_url())
        with self.assertRaises(ValueExtractionError):
            self.record.source_url

    def test_url_prefers_iaid_over_reference_number_and_source_url(self):
        record = Record(
            {
                "@template": {
                    "details": {
                        "iaid": "e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
                        "referenceNumber": "2515/300/1",
                        "sourceUrl": "https://www.example.com",
                    }
                }
            }
        )
        self.assertEqual(
            record.url,
            reverse("details-page-machine-readable", kwargs={"iaid": record.iaid}),
        )

    def test_url_prefers_reference_number_over_source_url(self):
        record = Record(
            {
                "@template": {
                    "details": {
                        "referenceNumber": "2515/300/1",
                        "sourceUrl": "https://www.example.com",
                    }
                }
            }
        )
        self.assertEqual(
            record.url,
            reverse(
                "details-page-human-readable",
                kwargs={"reference_number": record.reference_number},
            ),
        )

    def test_url_uses_source_url_when_no_iaid_or_reference_number_is_available(self):
        record = Record(
            {
                "@template": {
                    "details": {
                        "sourceUrl": "https://www.example.com",
                    }
                }
            }
        )
        self.assertEqual(record.url, record.source_url)

    def test_url_returns_blank_string_when_no_sutiable_data_is_present(self):
        record = Record(
            {
                "@template": {
                    "details": {
                        "summaryTitle": "A very incomplete record",
                    }
                }
            }
        )
        self.assertEqual(record.url, "")

    def test_description(self):
        self.assertEqual(
            self.record.description,
            (
                '<span class="scopecontent"><p>This series contains papers concering a wide variety of legal matters referred '
                "to the Law Officers for their advice or approval and includes applications for the "
                "Attorney General's General Fiat for leave to appeal to the House of Lords in criminal "
                "cases.</p><p>Also included are a number of opinions, more of which can be found in "
                '<a class="extref" href="C10298">LO 3</a></p></span>'
            ),
        )

    def test_listing_description(self):
        self.assertEqual(
            self.record.listing_description,
            (
                "\nThis series contains papers concering a wide variety of legal matters referred "
                "to the Law Officers for their advice or approval and includes applications for the "
                "Attorney General's General Fiat for leave to appeal to the House of Lords in criminal "
                "cases."
                "\nAlso included are a number of opinions, more of which can be found in LO 3"
            ),
        )

    def test_date_created(self):
        self.assertEqual(self.record.date_created, "1885-1979")

    def test_legal_status(self):
        self.assertEqual(self.record.legal_status, "Public Record(s)")

    def test_held_by(self):
        self.assertEqual(self.record.held_by, "The National Archives, Kew")

    def test_parent(self):
        r = self.record.parent
        self.assertEqual(
            (r.iaid, r.reference_number, r.summary_title),
            (
                "C199",
                "LO",
                "Records created or inherited by the Law Officers' Department",
            ),
        )

    def test_hierarchy(self):
        self.assertEqual(
            [
                (r.level_code, r.reference_number, r.summary_title)
                for r in self.record.hierarchy
            ],
            [
                (
                    None,
                    "LO",
                    "Records created or inherited by the Law Officers' Department",
                ),
                (
                    None,
                    "LO 2",
                    "Law Officers' Department: Registered Files",
                ),
                (
                    None,
                    "ADM 171",
                    "Admiralty, and Ministry of Defence, Navy Department: Medal Rolls",
                ),
            ],
        )

    def test_is_digitised_returns_false_when_data_not_present(self):
        self.assertEqual(self.record.is_digitised, False)

    def test_is_digitised_returns_true_when_true_value_present(self):
        # patch raw data
        self.record._raw["digitised"] = True
        self.assertEqual(self.record.is_digitised, True)

    def test_is_digitised_returns_false_when_false_value_present(self):
        # patch raw data
        self.record._raw["digitised"] = False
        self.assertEqual(self.record.is_digitised, False)

    @unittest.skip("Data not supported for the json record")
    def test_delivery_option(self):
        self.assertEqual(self.record.delivery_option, "DigitizedDiscovery")

    @unittest.skip("Data not supported for the json record")
    def test_availability_delivery_surrogates(self):
        self.assertEqual(
            self.record.availability_delivery_surrogates,
            [
                {
                    "type": "surrogate",
                    "value": (
                        '<a target="_blank" href="http://www.thegenealogist.co.uk/non-conformist-records">'
                        "The Genealogist"
                        "</a>"
                    ),
                },
                {
                    "type": "surrogate",
                    "value": (
                        '<a target="_blank" href="http://search.ancestry.co.uk/search/db.aspx?dbid=5111">'
                        "Ancestry"
                        "</a>"
                    ),
                },
            ],
        )

    def test_is_tna_default(self):
        # The test fixture includes the following, so this should
        # return True by default
        self.assertIs(self.record.is_tna, True)

    def test_is_tna_returns_false_if_group_is_non_tna(self):
        # patch raw data
        for group in self.record._raw["@datatype"]["group"]:
            if group["value"] == "tna":
                group["value"] = "nonTna"
        self.assertIs(self.record.is_tna, False)

    def test_is_tna_returns_false_if_datatype_not_present(self):
        # patch raw data
        self.record._raw.pop("@datatype")
        self.assertIs(self.record.is_tna, False)

    @unittest.skip("Data not supported for the json record")
    def test_topics(self):
        self.assertEqual(
            self.record.topics,
            [
                {
                    "title": "Taxonomy One",
                },
                {
                    "title": "Taxonomy Two",
                },
                {
                    "title": "Taxonomy Three",
                },
            ],
        )

    def test_next_record(self):
        r = self.record.next_record
        self.assertEqual(
            (r.iaid, r.reference_number, r.summary_title),
            ("C10298", "LO 1", "Law Officers' Department: Law Officers' Opinions"),
        )

    def test_previous_record(self):
        r = self.record.previous_record
        self.assertEqual(
            (r.iaid, r.reference_number, r.summary_title),
            ("C10296", "LO 3", "Law Officers' Department: Patents for Inventions"),
        )

    @unittest.skip("Data not supported for the json record")
    def test_related_records(self):
        self.assertEqual(
            [(r.iaid, r.summary_title) for r in self.record.related_records],
            [
                (
                    "C8981250",
                    "[1580-1688]. Notes (cards) from State Papers Foreign, Royal "
                    "Letters, SP 102/61. Manuscript.",
                )
            ],
        )

    @unittest.skip("Data not supported for the json record")
    def test_related_articles(self):
        self.assertEqual(
            [(r.summary_title, r.url) for r in self.record.related_articles],
            [
                (
                    "Irish maps c.1558-c.1610",
                    (
                        "http://www.nationalarchives.gov.uk/help-with-your-research/research-guides/"
                        "irish-maps-c1558-c1610/"
                    ),
                )
            ],
        )

    def test_source_catalogue(self):
        self.assertEqual(self.record.source, "CAT")

    def test_repo_summary_title(self):
        self.assertEqual(self.record.repo_summary_title, "The National Archives")

    def test_repo_archon_value(self):
        self.assertEqual(self.record.repo_archon_value, "66")

    def test_level_code(self):
        self.assertEqual(self.record.level_code, 3)

    def test_level(self):
        self.assertEqual(self.record.level, "Series")

    def test_related_materials(self):
        self.assertEqual(
            self.record.related_materials,
            (
                {
                    "description": "For files of the tri-service Defence Intelligence staff see,",
                    "links": [
                        {
                            "id": "C5789",
                            "text": "DEFE 31",
                            "href": "/catalogue/id/C5789/",
                        }
                    ],
                },
                {
                    "description": "For records of the Joint Intelligence Bureau see",
                    "links": [
                        {
                            "id": "C14457",
                            "text": "WO 252",
                            "href": "/catalogue/id/C14457/",
                        }
                    ],
                },
                {
                    "description": "Records of the Government Code and Cypher School:",
                    "links": [],
                },
            ),
        )

    def test_repository_attr(self):
        self.assertEqual(self.record.repository.iaid, "A13530124")
        self.assertEqual(self.record.repository.url, "/catalogue/id/A13530124/")


@override_settings(KONG_CLIENT_BASE_URL="https://kong.test")
class UnexpectedParsingIssueTest(SimpleTestCase):
    """A collection of tests verifying fixes for real-world (but unexpected)
    issues with data returned by Kong"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.records_client = get_records_client()

    @responses.activate
    def test_hierarchy_with_no_identifier_is_skipped(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="C123456",
                        hierarchy=[
                            {
                                "@summary": {
                                    "title": (
                                        "Foreign and Commonwealth Office and predecessors: "
                                        "Cultural Relations Departments:..."
                                    )
                                },
                            },
                        ],
                    ),
                ]
            ),
        )

        record = self.records_client.fetch(iaid="C123456")

        self.assertEqual(record.hierarchy, ())

    @responses.activate
    def test_record_with_origination_but_no_date(self):
        record = create_record(
            iaid="C123456",
        )
        del record["_source"]["origination"]["date"]

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(records=[record]),
        )

        record = self.records_client.fetch(iaid="C123456")

        self.assertEqual(record.date_created, "")

    @responses.activate
    def test_related_record_with_no_identifier(self):
        record = create_record(
            related=[
                {
                    "@admin": {
                        "id": "C568",
                        "uuid": "216d37d3-eb15-3e76-99d2-bc9ee99104ce",
                    },
                    "@entity": "reference",
                    "@link": {
                        "note": {
                            "value": "For records originating in the Exchequer see"
                        },
                        "qualifier": "association",
                        "relationship": {"value": "related"},
                    },
                    "summary": {
                        "title": "Records of the Office of First Fruits and Tenths"
                    },
                }
            ],
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(records=[record]),
        )

        record = self.records_client.fetch(iaid="C123456")

        # Related records with no 'identifer' and therefore no
        # reference_nubmers were skipped but now we're linking to the details
        # page using the iaid, these records should be present
        self.assertEqual(
            [(r.iaid, r.summary_title) for r in record.related_records],
            [
                ("C568", "Records of the Office of First Fruits and Tenths"),
            ],
        )

    @responses.activate
    def test_related_article_with_no_title(self):
        record = create_record(
            iaid="C123456",
            related=[
                {
                    "@admin": {
                        "id": "rg-1582",
                        "source": "wagtail-es",
                        "uuid": "890bc89e-9c9d-37a8-bdd4-1213bad92a33",
                    },
                    "@entity": "reference",
                    "@type": {"base": "media", "type": "research guide"},
                    "source": {
                        "location": (
                            "http://www.nationalarchives.gov.uk/"
                            "help-with-your-research/research-guides/famous-wills-1552-1854/"
                        )
                    },
                }
            ],
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(records=[record]),
        )

        record = self.records_client.fetch(iaid="C123456")

        self.assertEqual(record.related_articles, ())


@unittest.skip(
    "Kong open beta API does not support media. Re-enable/update once media is available."
)
@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class ImageTestCase(TestCase):
    @responses.activate
    def test_thumbnail_url(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[
                    create_media(
                        thumbnail_location="path/to/thumbnail.jpeg",
                        location="path/to/image.jpeg",
                    ),
                ]
            ),
        )

        images = Image.search.filter(rid="")
        image = images[0]

        self.assertEquals(
            image.thumbnail_url, "https://media.preview/path/to/thumbnail.jpeg"
        )

    @responses.activate
    def test_thumbnail_url_fallback(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[
                    create_media(
                        thumbnail_location=None, location="path/to/image.jpeg"
                    ),
                ]
            ),
        )

        images = Image.search.filter(rid="")
        image = images[0]

        # Fallback serves image through Wagtail instead of from kong
        self.assertEquals(image.thumbnail_url, "/records/image/path/to/image.jpeg")


@override_settings(KONG_CLIENT_BASE_URL="https://kong.test")
class ArchiveRecordModelTests(SimpleTestCase):
    """Record model tests for an Archive record"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.records_client = get_records_client()

    @responses.activate
    def test_source(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="A13532479",
                        source_values=[
                            {"source": {"value": "ARCHON"}},
                        ],
                    ),
                ]
            ),
        )

        record = self.records_client.fetch(iaid="A13532479")

        self.assertEqual(record.source, "ARCHON")

    @responses.activate
    def test_no_data_for_archive_attributes(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="A13532479",
                        source_values=[
                            {"source": {"value": "ARCHON"}},
                        ],
                    ),
                ]
            ),
        )

        record = self.records_client.fetch(iaid="A13532479")

        self.assertEqual(record.archive_contact_info, None)
        self.assertEqual(record.archive_further_info, None)
        self.assertEqual(record.archive_accessions, None)

    @responses.activate
    def test_title(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="A13532479",
                        source_values=[
                            {"source": {"value": "ARCHON"}},
                            {
                                "@template": {
                                    "details": {
                                        "title": "Some title value",
                                    }
                                }
                            },
                        ],
                    ),
                ]
            ),
        )

        record = self.records_client.fetch(iaid="A13532479")

        self.assertEqual(record.title, "Some title value")

    @responses.activate
    def test_archive_contact_info(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="A13532479",
                        source_values=[
                            {"source": {"value": "ARCHON"}},
                            {
                                "description": [
                                    {
                                        "ephemera": {
                                            "value": "<contacts><addressline1><![CDATA[this is line1]]></addressline1><addresstown><![CDATA[this town]]></addresstown><postcode><![CDATA[KW1 1AB]]></postcode><addresscountry><![CDATA[England]]></addresscountry><telephone><![CDATA[0123 456 789]]></telephone><fax><![CDATA[0321 456 789]]></fax><email><![CDATA[test@test.uk]]></email><url><![CDATA[https://www3.townshire.gov.uk/councilservices/archives-and-heritage/townshire-archives/Pages/default.aspx]]></url><mapURL><![CDATA[http://www.streetmap.co.uk/streetmap.dll?postcode2map?KW1 1AB]]></mapURL><contactpeople><contact><jobTitle><![CDATA[Manager]]></jobTitle><title><![CDATA[X]]></title><firstName><![CDATA[fname]]></firstName><lastName><![CDATA[lname]]></lastName></contact></contactpeople><correspaddr><![CDATA[this is corresp address]]></correspaddr></contacts>"
                                        },
                                    }
                                ]
                            },
                        ],
                    ),
                ]
            ),
        )

        record = self.records_client.fetch(iaid="A13532479")

        self.assertEqual(record.archive_contact_info.address_line1, "this is line1")
        self.assertEqual(record.archive_contact_info.address_town, "this town")
        self.assertEqual(record.archive_contact_info.postcode, "KW1 1AB")
        self.assertEqual(record.archive_contact_info.address_country, "England")
        self.assertEqual(
            record.archive_contact_info.map_url,
            "http://www.streetmap.co.uk/streetmap.dll?postcode2map?KW1 1AB",
        )
        self.assertEqual(
            record.archive_contact_info.url,
            "https://www3.townshire.gov.uk/councilservices/archives-and-heritage/townshire-archives/Pages/default.aspx",
        )
        self.assertEqual(record.archive_contact_info.telephone, "0123 456 789")
        self.assertEqual(record.archive_contact_info.fax, "0321 456 789")
        self.assertEqual(record.archive_contact_info.email, "test@test.uk")
        self.assertEqual(
            record.archive_contact_info.corresp_addr, "this is corresp address"
        )
        self.assertEqual(record.archive_contact_info.contact_job_title, "Manager")
        self.assertEqual(record.archive_contact_info.contact_title, "X")
        self.assertEqual(record.archive_contact_info.contact_first_name, "fname")
        self.assertEqual(record.archive_contact_info.contact_last_name, "lname")

    @responses.activate
    def test_archive_further_info(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="A13532479",
                        source_values=[
                            {"source": {"value": "ARCHON"}},
                            {
                                "place": [
                                    {
                                        "description": {
                                            "value": '<accessconditions><openinghours><![CDATA[this is opening hours]]></openinghours><holidays><![CDATA[this is holidays]]></holidays><disabledaccess>this is disabled access</disabledaccess><comments><![CDATA[<b>this is comments with html tags</b><a href="http://www.northamptonshire.gov.uk/heritage" target="_blank">website</a>]]></comments><researchservice>this is research service</researchservice><appointment>this is appointment</appointment><ticket>this is ticket</ticket><idrequired>this is idrequired</idrequired><fee>this is fee</fee></accessconditions>'
                                        },
                                    }
                                ]
                            },
                        ],
                    ),
                ]
            ),
        )

        record = self.records_client.fetch(iaid="A13532479")

        self.assertEqual(
            record.archive_further_info.opening_hours, "this is opening hours"
        )
        self.assertEqual(record.archive_further_info.holidays, "this is holidays")
        self.assertEqual(
            record.archive_further_info.facilities,
            [
                "this is disabled access",
                "this is research service",
                "this is appointment",
                "this is ticket",
                "this is idrequired",
                "this is fee",
            ],
        )
        self.assertEqual(
            record.archive_further_info.comments,
            """<b>this is comments with html tags</b><a href=\"http://www.northamptonshire.gov.uk/heritage\" target=\"_blank\">website</a>""",
        )

    @responses.activate
    def test_archive_collection_record_creators(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="A13532479",
                        source_values=[
                            {"source": {"value": "ARCHON"}},
                            {
                                "links": [
                                    {
                                        "@admin": {
                                            "id": "F169344",
                                        },
                                        "identifier": [{"value": "B"}],
                                        "name": {
                                            "value": "A Bell & Co Ltd, fireplace manufacturers, builders' merchants and ironmongers"
                                        },
                                        "place": {
                                            "name": [
                                                {
                                                    "value": "Kingsthorpe, Northamptonshire"
                                                }
                                            ]
                                        },
                                        "summary": {
                                            "title": "A Bell & Co Ltd, fireplace manufacturers, builders' merchants and ironmongers"
                                        },
                                    },
                                    {
                                        "@admin": {
                                            "id": "F109065",
                                        },
                                        "identifier": [{"value": "O"}],
                                        "place": {
                                            "name": [
                                                {"value": "Abbeycwmhir, Radnorshire"}
                                            ]
                                        },
                                        "summary": {"title": "Abbey Cwmhir Abbey"},
                                    },
                                    {
                                        "@admin": {
                                            "id": "F77667",
                                        },
                                        "identifier": [{"value": "P"}],
                                        "place": {
                                            "name": [
                                                {"value": "Kettering, Northamptonshire"}
                                            ]
                                        },
                                        "summary": {
                                            "title": "Abbott, Charles Henry Herbert, (1910-1977), diarist"
                                        },
                                    },
                                    {
                                        "@admin": {
                                            "id": "F30530",
                                        },
                                        "identifier": [{"value": "D"}],
                                        "place": {
                                            "name": [
                                                {"value": "Blisworth, Northamptonshire"}
                                            ]
                                        },
                                        "summary": {
                                            "title": "Allen, Lily May, (1888-1982), Schoolteacher"
                                        },
                                    },
                                    {
                                        "@admin": {
                                            "id": "F23087",
                                        },
                                        "@entity": "reference",
                                        "identifier": [{"value": "F"}],
                                        "place": {
                                            "name": [
                                                {
                                                    "value": "Harlestone, Northamptonshire;Daventry, Northamptonshire;Great Creaton, Northamptonshire;Upper Shuckburgh, Warwickshire"
                                                }
                                            ]
                                        },
                                        "summary": {
                                            "title": "Andrew family of Harlestone"
                                        },
                                    },
                                ]
                            },
                        ],
                    ),
                ]
            ),
        )

        record = self.records_client.fetch(iaid="A13532479")

        self.assertEqual(
            record.archive_collections.collection_info_list[0].name, "business"
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[0].display_name,
            "Businesses",
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[0].long_display_name,
            "Businesses",
        )
        self.assertEqual(record.archive_collections.collection_info_list[0].count, 1)
        self.assertEqual(
            record.archive_collections.collection_info_list[0].info_list,
            [
                {
                    "place": "Kingsthorpe, Northamptonshire",
                    "summary_title": "A Bell & Co Ltd, fireplace manufacturers, builders' merchants and ironmongers",
                    "url": "/catalogue/id/F169344/",
                }
            ],
        )

        self.assertEqual(
            record.archive_collections.collection_info_list[1].name, "organisation"
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[1].display_name,
            "Organisations",
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[1].long_display_name,
            "Organisations",
        )
        self.assertEqual(record.archive_collections.collection_info_list[1].count, 1)
        self.assertEqual(
            record.archive_collections.collection_info_list[1].info_list,
            [
                {
                    "place": "Abbeycwmhir, Radnorshire",
                    "summary_title": "Abbey Cwmhir Abbey",
                    "url": "/catalogue/id/F109065/",
                }
            ],
        )

        self.assertEqual(
            record.archive_collections.collection_info_list[2].name, "person"
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[2].display_name, "Persons"
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[2].long_display_name,
            "Persons",
        )
        self.assertEqual(record.archive_collections.collection_info_list[2].count, 1)
        self.assertEqual(
            record.archive_collections.collection_info_list[2].info_list,
            [
                {
                    "place": "Kettering, Northamptonshire",
                    "summary_title": "Abbott, Charles Henry Herbert, (1910-1977), diarist",
                    "url": "/catalogue/id/F77667/",
                }
            ],
        )

        self.assertEqual(
            record.archive_collections.collection_info_list[3].name, "diary"
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[3].display_name, "Diaries"
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[3].long_display_name,
            "Diaries",
        )
        self.assertEqual(record.archive_collections.collection_info_list[3].count, 1)
        self.assertEqual(
            record.archive_collections.collection_info_list[3].info_list,
            [
                {
                    "place": "Blisworth, Northamptonshire",
                    "summary_title": "Allen, Lily May, (1888-1982), Schoolteacher",
                    "url": "/catalogue/id/F30530/",
                }
            ],
        )

        self.assertEqual(
            record.archive_collections.collection_info_list[4].name, "family"
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[4].display_name, "Families"
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[4].long_display_name,
            "Families",
        )
        self.assertEqual(record.archive_collections.collection_info_list[4].count, 1)
        self.assertEqual(
            record.archive_collections.collection_info_list[4].info_list,
            [
                {
                    "place": "Harlestone, Northamptonshire;Daventry, Northamptonshire;Great Creaton, Northamptonshire;Upper Shuckburgh, Warwickshire",
                    "summary_title": "Andrew family of Harlestone",
                    "url": "/catalogue/id/F23087/",
                }
            ],
        )

    @responses.activate
    def test_archive_nra_records_info(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="A13532479",
                        source_values=[
                            {"source": {"value": "ARCHON"}},
                            {
                                "manifestations": [
                                    {
                                        "identifier": [
                                            {"value": "9358"},
                                        ],
                                        "title": [
                                            {
                                                "value": "Adnitt Road Baptist Church, Northampton"
                                            }
                                        ],
                                        "url": "SCANNED_LIST",
                                    },
                                ]
                            },
                        ],
                    ),
                ]
            ),
        )

        record = self.records_client.fetch(iaid="A13532479")

        self.assertEqual(
            record.archive_collections.collection_info_list[0].name, "paper_catalogue"
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[0].display_name,
            "Paper catalogues",
        )
        self.assertEqual(
            record.archive_collections.collection_info_list[0].long_display_name,
            "Paper catalogues available to view at The National Archives",
        )
        self.assertEqual(record.archive_collections.collection_info_list[0].count, 1)
        self.assertEqual(
            record.archive_collections.collection_info_list[0].info_list,
            [
                {
                    "identifier_title": "NRA 9358 Adnitt Road Baptist Church, Northampton",
                    "url": "SCANNED_LIST",
                }
            ],
        )

    @responses.activate
    def test_archive_accessions(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="A13532479",
                        source_values=[
                            {"source": {"value": "ARCHON"}},
                            {
                                "@template": {
                                    "details": {
                                        "referenceNumber": "154",
                                        "accumulationDates": "<accessionyears><accessionyear>1998</accessionyear><accessionyear>2013</accessionyear></accessionyears>",
                                    }
                                }
                            },
                        ],
                    ),
                ]
            ),
        )

        record = self.records_client.fetch(iaid="A13532479")

        self.assertEqual(
            record.archive_accessions.accession_years,
            {
                "1998": "https://www.nationalarchives.gov.uk/accessions/1998/98returns/98ac154.htm",
                "2013": "https://www.nationalarchives.gov.uk/accessions/2013/13returns/13ac154.htm",
            },
        )

    @responses.activate
    def test_archive_repository_url(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="A13532479",
                        source_values=[
                            {"source": {"value": "ARCHON"}},
                            {"repository": {"url": "http://nro.adlibhosting.com/"}},
                        ],
                    ),
                ]
            ),
        )

        record = self.records_client.fetch(iaid="A13532479")

        self.assertEqual(record.archive_repository_url, "http://nro.adlibhosting.com/")
