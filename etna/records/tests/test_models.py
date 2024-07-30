import json
import unittest

from copy import deepcopy

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from django.utils.safestring import SafeString

import responses

from ...ciim.tests.factories import create_record, create_response
from ...ciim.utils import ValueExtractionError
from ..api import get_records_client
from ..models import Record


class DefaultReturnsRecordModelTests(SimpleTestCase):
    response = {"data": {"@template": {"details": {"someattribute": "somevalue"}}}}

    def setUp(self):
        self.record = Record(self.response)

    def test_template_defaults_when_no_attribute_is_present(self):
        # patch raw data
        self.record._raw["data"]["@template"]["details"] = {}
        self.assertEqual(self.record.description, "")
        self.assertEqual(self.record.summary, "")
        self.assertEqual(self.record.title, "")
        self.assertEqual(self.record.date_created, "")
        self.assertEqual(self.record.uuid, "")
        self.assertEqual(self.record.group, "")
        self.assertEqual(self.record.identifier, "")
        self.assertEqual(self.record.ciim_id, "")
        self.assertEqual(self.record.ciim_url, "")
        self.assertEqual(self.record.collection, "")
        self.assertEqual(self.record.collection_id, "")
        self.assertEqual(self.record.rights, "")
        self.assertEqual(self.record.subjects, [])
        self.assertEqual(self.record.community_collection, {})
        self.assertEqual(self.record.community_collection_webpage, {})


class CommunityRecordModelTests(SimpleTestCase):
    maxDiff = None
    fixture_path = f"{settings.BASE_DIR}/etna/ciim/tests/fixtures/record_community.json"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.records_client = get_records_client()
        with open(cls.fixture_path, "r") as f:
            cls.fixture_contents = json.loads(f.read())

    def setUp(self):
        self.record = Record(deepcopy(self.fixture_contents["data"]))

    def test_template_uses_detail_template_when_present(self):
        self.assertIn("details", self.record._raw["@template"])
        self.assertEqual(self.record.template, self.record._raw["@template"]["details"])

    def test_template_returns_empty_dict_when_no_template_available(self):
        # patch raw data
        self.record._raw["@template"] = {}
        self.assertEqual(self.record.template, {})

    def test_uuid(self):
        self.assertEqual(self.record.uuid, "f4a6014d-cf22-3a88-ba1b-765622f25319")

    def test_description(self):
        self.assertEqual(self.record.description, "data for description")

    def test_description_contains_html(self):
        # patch raw data
        value_contains_html = '<b> in bold </b> <p> in para </p><span>in span<a href="http://test.com">atag</a></span><custom>custom tag</custom>\nline2'
        self.record._raw["@template"]["details"].update(
            {"description": value_contains_html}
        )
        self.assertEqual(
            self.record.description,
            'in bold  <p> in para </p>in span<a href="http://test.com" rel="noopener noreferrer">atag</a>custom tag<br>line2',
        )

    def test_group(self):
        self.assertEqual(self.record.group, "community")

    def test_identifier(self):
        self.assertEqual(self.record.identifier, "data for identifier")

    def test_ciim_id(self):
        self.assertEqual(self.record.ciim_id, "pcw-12345")

    def test_ciim_url(self):
        self.assertEqual(
            self.record.ciim_url,
            reverse(
                "details-page-machine-readable", kwargs={"id": self.record.ciim_id}
            ),
        )

    def test_collection_id(self):
        self.assertEqual(self.record.collection_id, "pcw-7890")

    def test_item_url(self):
        self.assertEqual(self.record.item_url, "https://www.test.url")

    def test_location(self):
        self.assertEqual(self.record.location, "data for location")

    def test_format(self):
        self.assertEqual(self.record.format, "data for format")

    def test_rights(self):
        self.assertEqual(self.record.rights, "data for rights")

    def test_title(self):
        self.assertEqual(self.record.title, "data for title")

    def test_summary(self):
        self.assertEqual(self.record.summary, "data for summary")

    def test_summary_title(self):
        self.assertEqual(self.record.summary_title, "data for summary")

    def test_has_enrichment_true(self):
        self.assertEqual(self.record.has_enrichment, True)

    def test_has_enrichment_false(self):
        # patch raw data
        del self.record._raw["@template"]["details"]["enrichment"]
        self.assertEqual(self.record.has_enrichment, False)

    def test_enrichment_loc(self):
        self.assertEqual(
            self.record.enrichment_loc,
            [
                {
                    "value": "some location value 1",
                    "url": "https://www.wikidata.org/wiki/1",
                },
                {
                    "value": "some location value 2",
                    "url": "https://www.wikidata.org/wiki/2",
                },
                {
                    "value": "some location value 3",
                    "url": "https://www.wikidata.org/wiki/3",
                },
                {
                    "value": "some location value 4",
                    "url": "https://www.wikidata.org/wiki/4",
                },
                {
                    "value": "some location value 5",
                    "url": "https://www.wikidata.org/wiki/5",
                },
                {
                    "value": "some location value 6",
                    "url": "https://www.wikidata.org/wiki/6",
                },
            ],
        )

    def test_enrichment_loc_with_value_no_url_attr(self):
        self.record._raw["@template"]["details"]["enrichment"] = {
            "loc": [
                {
                    "value": "some location value without url",
                },
            ]
        }
        self.assertEqual(
            self.record.enrichment_loc,
            [
                {
                    "value": "some location value without url",
                }
            ],
        )
        self.assertIsNone(self.record.enrichment_loc[0].get("url"))

    def test_enrichment_loc_not_wiki_url(self):
        self.record._raw["@template"]["details"]["enrichment"] = {
            "loc": [
                {
                    "value": "some location value with invalid url",
                    "url": "https://www.notawiki.org/wiki/123",
                },
            ]
        }
        with self.assertRaisesMessage(
            ValidationError,
            "https://www.notawiki.org/wiki/123 value is not a valid wikidata URL.",
        ):
            _ = self.record.enrichment_loc

    def test_enrichment_per(self):
        self.assertEqual(
            self.record.enrichment_per,
            [
                {
                    "value": "some person value 1",
                    "url": "https://www.wikidata.org/wiki/8",
                }
            ],
        )

    def test_enrichment_org(self):
        self.assertEqual(
            self.record.enrichment_org,
            [
                {
                    "value": "some organisation value 1",
                    "url": "https://www.wikidata.org/wiki/7",
                }
            ],
        )

    def test_enrichment_misc(self):
        self.assertEqual(
            self.record.enrichment_misc,
            [{"value": "some misc value 1", "url": "https://www.wikidata.org/wiki/9"}],
        )

    def test_enrichment_date(self):
        self.assertEqual(
            self.record.enrichment_date,
            [
                {"value": "1936", "url": "https://www.wikidata.org/wiki/11"},
                {"value": "1925", "url": "https://www.wikidata.org/wiki/12"},
            ],
        )

    def test_description_for_swop(self):
        self.record._raw["@template"]["details"]["ciimId"] = "swop-1234"
        self.record._raw["@template"]["details"][
            "descriptionPlace"
        ] = "data for descriptionPlace"
        self.record._raw["@template"]["details"][
            "descriptionView"
        ] = "data for descriptionView"
        self.assertEqual(
            self.record.description,
            "data for descriptionPlace" + " " + "data for descriptionView",
        )

    def test_description_for_swop_partial_data(self):
        self.record._raw["@template"]["details"]["ciimId"] = "swop-1234"
        self.record._raw["@template"]["details"][
            "descriptionView"
        ] = "data for descriptionView"
        self.assertEqual(self.record.description, "data for descriptionView")

    def test_provenance(self):
        self.assertEqual(self.record.provenance, "data for provenance")

    def test_creator(self):
        self.assertEqual(self.record.creator, "data for creator")

    def test_repository(self):
        self.assertEqual(self.record.repository, "data for repository")


class CommunityRecordCollectionAttrTests(SimpleTestCase):
    maxDiff = None

    def test_collection_attrs(self):
        test_data = (
            (
                # label
                "missing collection attr",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "swop-2897",
                            "level": "Item",
                            "collectionId": "swop-0",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {"community_collection": {}, "community_collection_webpage": {}},
            ),
            (
                # label
                "swop: Item level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "swop-2897",
                            "level": "Item",
                            "collectionId": "swop-0",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Community archive",
                        "value": "some value",
                        "url": "https://swop.org.uk/",
                        "is_ext_url": True,
                    },
                    "community_collection_webpage": {},
                },
            ),
            (
                # label
                "swop: Community level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "swop-0",
                            "level": "Community",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {},
                    "community_collection_webpage": {},
                },
            ),
            (
                # label
                "pcw: Item level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "pcw-383261",
                            "level": "Item",
                            "collectionId": "pcw-0",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Community archive",
                        "value": "some value",
                        "url": "https://www.peoplescollection.wales/",
                        "is_ext_url": True,
                    },
                    "community_collection_webpage": {},
                },
            ),
            (
                # label
                "pcw: Community level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "pcw-0",
                            "level": "Community",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {},
                    "community_collection_webpage": {},
                },
            ),
            (
                # label
                "shc: Item level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "shc-9967-1-18",
                            "level": "Item",
                            "collectionId": "shc-9967-1",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Collection",
                        "value": "some value",
                        "url": "/catalogue/id/shc-9967-1/",
                        "is_ext_url": False,
                    },
                    "community_collection_webpage": {
                        "label": "Community archive",
                        "value": "Surrey History Centre",
                        "url": "https://www.surreyarchives.org.uk/",
                    },
                },
            ),
            (
                # label
                "shc: Series level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "shc-9967-1",
                            "level": "Series",
                            "collectionId": "shc-9967",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Collection",
                        "value": "some value",
                        "url": "/catalogue/id/shc-9967/",
                        "is_ext_url": False,
                    },
                    "community_collection_webpage": {
                        "label": "Community archive",
                        "value": "Surrey History Centre",
                        "url": "https://www.surreyarchives.org.uk/",
                    },
                },
            ),
            (
                # label
                "shc: Collection level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "shc-9967",
                            "level": "Collection",
                            "collectionId": "shc-0",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Community archive",
                        "value": "some value",
                        "url": "https://www.surreyarchives.org.uk/",
                        "is_ext_url": True,
                    },
                    "community_collection_webpage": {},
                },
            ),
            (
                # label
                "shc: Community level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "shc-0",
                            "level": "Community",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {},
                    "community_collection_webpage": {},
                },
            ),
            (
                # label
                "mpa: Item level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "mpa-13090",
                            "level": "Item",
                            "collectionId": "mpa-9",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Collection",
                        "value": "some value",
                        "url": "/catalogue/id/mpa-9/",
                        "is_ext_url": False,
                    },
                    "community_collection_webpage": {
                        "label": "Community archive",
                        "value": "Morrab Photo Archive",
                        "url": "https://photoarchive.morrablibrary.org.uk/",
                    },
                },
            ),
            (
                # label
                "mpa: Series level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "mpa-12345",
                            "level": "Series",
                            "collectionId": "mpa-6789",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Collection",
                        "value": "some value",
                        "url": "/catalogue/id/mpa-6789/",
                        "is_ext_url": False,
                    },
                    "community_collection_webpage": {
                        "label": "Community archive",
                        "value": "Morrab Photo Archive",
                        "url": "https://photoarchive.morrablibrary.org.uk/",
                    },
                },
            ),
            (
                # label
                "mpa: Collection level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "mpa-9",
                            "level": "Collection",
                            "collectionId": "mpa-0",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Community archive",
                        "value": "some value",
                        "url": "https://photoarchive.morrablibrary.org.uk/",
                        "is_ext_url": True,
                    },
                    "community_collection_webpage": {},
                },
            ),
            (
                # label
                "mpa: Community level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "mpa-0",
                            "level": "Community",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {},
                    "community_collection_webpage": {},
                },
            ),
            (
                # label
                "wmk: Item level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "wmk-20501",
                            "level": "Item",
                            "collectionId": "wmk-20469",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Collection",
                        "value": "some value",
                        "url": "/catalogue/id/wmk-20469/",
                        "is_ext_url": False,
                    },
                    "community_collection_webpage": {
                        "label": "Community archive",
                        "value": "Milton Keynes City Discovery Centre",
                        "url": "https://catalogue.mkcdc.org.uk/",
                    },
                },
            ),
            (
                # label
                "wmk: Series level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "wmk-12345",
                            "level": "Series",
                            "collectionId": "wmk-6789",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Collection",
                        "value": "some value",
                        "url": "/catalogue/id/wmk-6789/",
                        "is_ext_url": False,
                    },
                    "community_collection_webpage": {
                        "label": "Community archive",
                        "value": "Milton Keynes City Discovery Centre",
                        "url": "https://catalogue.mkcdc.org.uk/",
                    },
                },
            ),
            (
                # label
                "wmk: Collection level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "wmk-6789",
                            "level": "Collection",
                            "collectionId": "wmk-0",
                            "collection": "some value",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {
                        "label": "Community archive",
                        "value": "some value",
                        "url": "https://catalogue.mkcdc.org.uk/",
                        "is_ext_url": True,
                    },
                    "community_collection_webpage": {},
                },
            ),
            (
                # label
                "wmk: Community level",
                # value
                {
                    "@template": {
                        "details": {
                            "ciimId": "wmk-0",
                            "level": "Community",
                            "group": "community",
                            "description": "description",
                        }
                    }
                },
                # expected
                {
                    "community_collection": {},
                    "community_collection_webpage": {},
                },
            ),
        )
        for label, data, expected in test_data:
            with self.subTest(label):
                self.record = Record(raw_data=data)
                # test collection attr updates in template
                self.assertEqual(
                    self.record.community_collection,
                    expected.get("community_collection"),
                )
                # test data used to add a new row in template
                self.assertEqual(
                    self.record.community_collection_webpage,
                    expected.get("community_collection_webpage"),
                )


@unittest.skip("TODO:Rosetta")
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
        self.record._raw["@template"]["details"].pop("primaryIdentifier")
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

    def test_url_prefers_reference_number_over_iaid_and_source_url(self):
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
            reverse(
                "details-page-human-readable",
                kwargs={"reference_number": record.reference_number},
            ),
        )

    def test_url_prefers_iaid_over_source_url(self):
        record = Record(
            {
                "@template": {
                    "details": {
                        "iaid": "e7e92a0b-3666-4fd6-9dac-9d9530b0888c",
                        "sourceUrl": "https://www.example.com",
                    }
                }
            }
        )
        self.assertEqual(
            record.url,
            reverse(
                "details-page-machine-readable",
                kwargs={"id": record.iaid},
            ),
        )

    def test_url_uses_source_url_when_reference_number_and_iaid_are_missing(self):
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

    def test_no_reference_number_url_prefers_iaid_over_reference_number(self):
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
            record.non_reference_number_url,
            reverse(
                "details-page-machine-readable",
                kwargs={"id": record.iaid},
            ),
        )

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
                "This series contains papers concering a wide variety of legal matters referred "
                "to the Law Officers for their advice or approval and includes applications for the "
                "Attorney General's General Fiat for leave to appeal to the House of Lords in criminal "
                "cases. "
                "Also included are a number of opinions, more of which can be found in LO 3"
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
        self.assertEqual(self.record.repository.url, "/catalogue/ref/66/")
        self.assertEqual(
            self.record.repository.non_reference_number_url, "/catalogue/id/A13530124/"
        )

    def test_closure_status_empty_value(self):
        self.assertEqual(self.record.closure_status, "")

    def test_closure_status_with_value(self):
        self.record = Record(
            raw_data={
                "@template": {
                    "details": {
                        "iaid": "C12345",
                        "closureStatus": "Some status value",
                    }
                }
            }
        )
        self.assertEqual(self.record.closure_status, "Some status value")


@unittest.skip("TODO:Rosetta")
@override_settings(CLIENT_BASE_URL=f"{settings.CLIENT_BASE_URL}")
class UnexpectedParsingIssueTest(SimpleTestCase):
    """A collection of tests verifying fixes for real-world (but unexpected)
    issues with data returned by Client API"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.records_client = get_records_client()

    @responses.activate
    def test_hierarchy_with_no_identifier_is_skipped(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
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

        record = self.records_client.get(id="C123456")

        self.assertEqual(record.hierarchy, ())

    @responses.activate
    def test_record_with_origination_but_no_date(self):
        record = create_record(
            iaid="C123456",
        )
        del record["_source"]["origination"]["date"]

        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(records=[record]),
        )

        record = self.records_client.get(id="C123456")

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
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(records=[record]),
        )

        record = self.records_client.get(id="C123456")

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
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(records=[record]),
        )

        record = self.records_client.get(id="C123456")

        self.assertEqual(record.related_articles, ())


@unittest.skip("TODO:Rosetta")
class RecordModelCatalogueTests(SimpleTestCase):
    maxDiff = None

    def setUp(self):
        self.source = {
            "@admin": {
                "id": "C123456",
            },
            "source": {"value": "CAT"},
            "@template": {
                "details": {
                    "iaid": "C123456",
                }
            },
        }

    def test_record_catalogue(self):
        self.record = Record(self.source)

        self.assertEqual(self.record.iaid, "C123456")
        self.assertEqual(self.record.custom_record_type, "CAT")

    def test_empty_for_optional_attributes(self):
        self.record = Record(self.source)

        self.assertEqual(self.record.arrangement, "")
        self.assertEqual(self.record.held_by_id, "")
        self.assertEqual(self.record.held_by_url, "")
        self.assertEqual(self.record.record_opening, "")
        self.assertEqual(self.record.title, "")
        self.assertEqual(self.record.creator, [])
        self.assertEqual(self.record.dimensions, "")
        self.assertEqual(self.record.former_department_reference, "")
        self.assertEqual(self.record.former_pro_reference, "")
        self.assertEqual(self.record.language, [])
        self.assertEqual(self.record.map_designation, "")
        self.assertEqual(self.record.map_scale, "")
        self.assertEqual(self.record.note, [])
        self.assertEqual(self.record.physical_condition, "")
        self.assertEqual(self.record.physical_description, "")
        self.assertEqual(self.record.accruals, "")
        self.assertEqual(self.record.accumulation_dates, "")
        self.assertEqual(self.record.appraisal_information, "")
        self.assertEqual(self.record.immediate_source_of_acquisition, [])
        self.assertEqual(self.record.administrative_background, "")
        self.assertEqual(self.record.separated_materials, ())
        self.assertEqual(self.record.unpublished_finding_aids, [])
        self.assertEqual(self.record.copies_information, [])
        self.assertEqual(self.record.custodial_history, "")
        self.assertEqual(self.record.location_of_originals, [])
        self.assertEqual(self.record.restrictions_on_use, "")
        self.assertEqual(self.record.publication_note, [])
        self.assertEqual(self.record.delivery_option, "")

    def test_held_by_url_attrs(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "heldById": "A13530124",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.held_by_id, "A13530124")
        self.assertEqual(self.record.held_by_url, "/catalogue/id/A13530124/")

    def test_arrangement(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "arrangement": "<arrangement><p>Former reference order within two accessions (AN 171/1-648 and AN 171/649-970). </p></arrangement>",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertTrue(isinstance(self.record.arrangement, SafeString))
        self.assertEqual(
            self.record.arrangement,
            "<arrangement><p>Former reference order within two accessions (AN 171/1-648 and AN 171/649-970). </p></arrangement>",
        )

    def test_record_opening(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "recordOpening": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.record_opening, "some value")

    def test_title(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "title": '<span class="unittitle" type="Title">Records of the General Register Office, Government Social Survey Department, and Office of Population Censuses and Surveys</span>',
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertTrue(isinstance(self.record.title, SafeString))
        self.assertEqual(
            self.record.title,
            '<span class="unittitle" type="Title">Records of the General Register Office, Government Social Survey Department, and Office of Population Censuses and Surveys</span>',
        )

    def test_creator(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "creator": ["some value 1", "some value 2"],
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.creator, ["some value 1", "some value 2"])

    def test_dimensions(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "dimensions": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.dimensions, "some value")

    def test_former_department_reference(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "formerDepartmentReference": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.former_department_reference, "some value")

    def test_former_pro_reference(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "formerProReference": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.former_pro_reference, "some value")

    def test_language(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "language": ["some value 1", "some value 2"],
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.language, ["some value 1", "some value 2"])

    def test_map_designation(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "mapDesignation": '<unittitle type="Map Designation">some value</unittitle>',
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.map_designation,
            '<unittitle type="Map Designation">some value</unittitle>',
        )
        self.assertTrue(isinstance(self.record.map_designation, SafeString))

    def test_map_scale(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "mapScale": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.map_scale, "some value")

    def test_note(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "note": [
                            "Details have been added from C 32/18, which also gives information about further process. </p><p>",
                        ],
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.note,
            [
                "Details have been added from C 32/18, which also gives information about further process. </p><p>"
            ],
        )
        self.assertTrue(isinstance(self.record.note[0], SafeString))

    def test_physical_condition(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "physicalCondition": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.physical_condition, "some value")

    def test_physical_description(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "physicalDescription": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.physical_description, "some value")

    def test_accruals(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "accruals": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.accruals, "some value")

    def test_accumulation_dates(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "accumulationDates": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.accumulation_dates, "some value")

    def test_appraisal_information(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "appraisalInformation": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.appraisal_information, "some value")

    def test_immediate_source_of_acquisition(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "immediateSourceOfAcquisition": [
                            "some value 1",
                            "some value 2",
                        ],
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.immediate_source_of_acquisition,
            ["some value 1", "some value 2"],
        )

    def test_administrative_background(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "administrativeBackground": "<bioghist><bioghist><p>The Industrial Relations Department was set up as soon as the British Transport Commission began functioning and continued in existence until the end of the British Railway Board. In 1983 it was renamed Employee Relations Department.</p></bioghist></bioghist>",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertTrue(isinstance(self.record.administrative_background, SafeString))
        self.assertEqual(
            self.record.administrative_background,
            "<bioghist><bioghist><p>The Industrial Relations Department was set up as soon as the British Transport Commission began functioning and continued in existence until the end of the British Railway Board. In 1983 it was renamed Employee Relations Department.</p></bioghist></bioghist>",
        )

    def test_separated_materials(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "separatedMaterials": [
                            {
                                "description": "for 4 maps extracted from this item see",
                                "links": [
                                    '<a href="C8956177">MFQ 1/761/7</a>',
                                    '<a href="C8956176">MFQ 1/761/6</a>',
                                    '<a href="C8956175">MFQ 1/761/5</a>',
                                    '<a href="C8956174">MFQ 1/761/4</a>',
                                ],
                            }
                        ],
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.separated_materials,
            (
                {
                    "description": "for 4 maps extracted from this item see",
                    "links": [
                        {
                            "href": "/catalogue/id/C8956177/",
                            "id": "C8956177",
                            "text": "MFQ 1/761/7",
                        },
                        {
                            "href": "/catalogue/id/C8956176/",
                            "id": "C8956176",
                            "text": "MFQ 1/761/6",
                        },
                        {
                            "href": "/catalogue/id/C8956175/",
                            "id": "C8956175",
                            "text": "MFQ 1/761/5",
                        },
                        {
                            "href": "/catalogue/id/C8956174/",
                            "id": "C8956174",
                            "text": "MFQ 1/761/4",
                        },
                    ],
                },
            ),
        )

    def test_unpublished_finding_aids(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "unpublishedFindingAids": ["some value 1", "some value 2"],
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.unpublished_finding_aids, ["some value 1", "some value 2"]
        )

    def test_copies_information(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "copiesInformation": ["some value 1", "some value 2"],
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.copies_information, ["some value 1", "some value 2"]
        )

    def test_custodial_history(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "custodialHistory": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.custodial_history, "some value")

    def test_location_of_originals(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "locationOfOriginals": ["some value 1", "some value 2"],
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.location_of_originals, ["some value 1", "some value 2"]
        )

    def test_restrictions_on_use(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "restrictionsOnUse": "some value",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.restrictions_on_use, "some value")

    def test_publication_note(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "publicationNote": ["some value 1", "some value 2"],
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.publication_note, ["some value 1", "some value 2"])

    def test_delivery_option(self):
        self.source.update(
            {
                "@template": {
                    "details": {
                        "deliveryOption": "No availability condition provisioned for this record",
                    }
                },
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.delivery_option,
            "No availability condition provisioned for this record",
        )
