from django.test import SimpleTestCase

from ..models import Record


class RecordModelCreatorsTests(SimpleTestCase):
    def setUp(self):
        self.source = {
            "@admin": {
                "id": "F69594",
            },
            "identifier": [
                {
                    "faid": "F69594",
                    "primary": True,
                    "type": "faid",
                    "value": "F69594",
                },
            ],
            "@template": {
                "details": {
                    "primaryIdentifier": "F69594",
                }
            },
        }

    def test_record_creators(self):
        self.record = Record(self.source)

        self.assertEqual(self.record.iaid, "F69594")
        self.assertEqual(self.record.custom_record_type, "CREATORS")

    def test_record_creators_where_other_attributes_are_optionally_not_received(self):
        self.record = Record(self.source)

        self.assertEqual(self.record.iaid, "F69594")
        self.assertEqual(self.record.custom_record_type, "CREATORS")
        self.assertEqual(self.record.reference_number, "")
        self.assertEqual(self.record.alternative_names, ())
        self.assertEqual(self.record.first_name, "")
        self.assertEqual(self.record.last_name, "")
        self.assertEqual(self.record.title_prefix, "")
        self.assertEqual(self.record.title_for_name, "")
        self.assertEqual(self.record.gender, "")
        self.assertEqual(self.record.history, "")
        self.assertEqual(self.record.biography, {})
        self.assertEqual(self.record.func_occup_activ, "")
        self.assertEqual(self.record.places, ())
        self.assertEqual(self.record.birth_date, "")
        self.assertEqual(self.record.death_date, "")
        self.assertEqual(self.record.start_date, "")
        self.assertEqual(self.record.end_date, "")
        self.assertEqual(self.record.record_creators_date, "")
        self.assertEqual(self.record.name_authority_reference, "")
        self.assertEqual(self.record.former_name_authority_reference, "")

    def test_alternative_names(self):
        self.source.update(
            {
                "name": [
                    {"type": "maiden name", "value": "A maiden name value"},
                    {"type": "also known as", "value": "An also known as value"},
                    {"type": "formerly known as", "value": "A formerly known as value"},
                    {"type": "later known as", "value": "A later known as value"},
                    {"type": "pseudonym", "value": "A pseudonym value"},
                    {"type": "relation of", "value": "A relation of value"},
                    {"type": "real name", "value": "A real name value"},
                    {
                        "type": "standardised form of name according to other rules",
                        "value": "A standardised form of name according to other rules value",
                    },
                    {"type": "unknown / other", "value": "An unknown / other value"},
                ],
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.alternative_names,
            (
                {"label": "Maiden name", "value": "A maiden name value"},
                {"label": "Also known as", "value": "An also known as value"},
                {"label": "Formerly known as", "value": "A formerly known as value"},
                {"label": "Later known as", "value": "A later known as value"},
                {"label": "Pseudonym", "value": "A pseudonym value"},
                {"label": "Relation of", "value": "A relation of value"},
                {"label": "Real name", "value": "A real name value"},
                {
                    "label": "Standardised form of name according to other rules",
                    "value": "A standardised form of name according to other rules value",
                },
                {"label": "Unknown / Other", "value": "An unknown / other value"},
            ),
        )

    def test_first_name(self):
        self.source.update(
            {
                "name": [
                    {
                        "first_name": ["Firstname1", "Firstname2"],
                    }
                ],
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.first_name, "Firstname1 Firstname2")

    def test_last_name(self):
        self.source.update(
            {
                "name": [
                    {
                        "last_name": "Lastname",
                    }
                ],
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.last_name, "Lastname")

    def test_title_prefix(self):
        self.source.update(
            {
                "name": [
                    {
                        "title_prefix": "Sir",
                    }
                ],
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.title_prefix, "Sir")

    def test_title_for_name(self):
        self.source.update(
            {
                "name": [
                    {
                        "title": "This is title for name",
                    }
                ],
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.title_for_name, "This is title for name")

    def test_gender(self):
        gender_values = (
            ({"gender": "M"}, "Male"),
            ({"gender": "F"}, "Female"),
            ({"gender": "raw value"}, "raw value"),
        )
        for api_value, expected_value in gender_values:
            self.source.update(api_value)
            self.record = Record(self.source)
            self.assertEqual(self.record.gender, expected_value)

    def test_history(self):
        self.source.update(
            {
                "description": [
                    {
                        "primary": True,
                        "type": "history",
                        "value": "Life Vice-President, British Red Cross Society.<p></p>DBE 1946. GBE 1954.",
                    },
                ],
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.history,
            "Life Vice-President, British Red Cross Society.<p></p>DBE 1946. GBE 1954.",
        )

    def test_biography(self):
        self.source.update(
            {
                "description": [
                    {
                        "type": "biography",
                        "url": "http://dx.doi.org/10.1093/ref:odnb/31540",
                        "value": "ODNB link for Pery, Angela Olivia (1897-1981) nee Trotter, Vice President of British Red Cross Society, wife of 5th Earl of Limerick",
                    },
                ],
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.biography,
            {
                "value": "ODNB link for Pery, Angela Olivia (1897-1981) nee Trotter, Vice President of British Red Cross Society, wife of 5th Earl of Limerick",
                "url": "http://dx.doi.org/10.1093/ref:odnb/31540",
            },
        )

    def test_func_occup_activ(self):
        value_without_foa = {
            "description": [
                {
                    "type": "functions, occupations and activities",
                    "value": "Vice President of British Red Cross Society, wife of 5th Earl of Limerick",
                },
            ],
        }
        value_with_foa = {
            "description": [
                {
                    "type": "functions, occupations and activities",
                    "value": "<foa><![CDATA[Food, drink and tobacco > Brewing and malting]]></foa>",
                },
            ],
        }

        self.source.update(value_without_foa)
        self.record = Record(self.source)
        self.assertEqual(
            self.record.func_occup_activ,
            "Vice President of British Red Cross Society, wife of 5th Earl of Limerick",
        )

        del self.source["description"]
        self.source.update(value_with_foa)
        self.record = Record(self.source)
        self.assertEqual(
            self.record.func_occup_activ,
            "Food, drink and tobacco > Brewing and malting",
        )

    def test_places(self):
        self.source.update(
            {
                "place": [
                    {"name": [{"value": "Harmondsworth, Middlesex"}]},
                    {"name": [{"value": "Hillingdon, Middlesex"}]},
                    {"name": [{"value": "West Drayton, Middlesex"}]},
                ],
            }
        )
        self.record = Record(self.source)

        self.assertEqual(
            self.record.places,
            (
                "Harmondsworth, Middlesex",
                "Hillingdon, Middlesex",
                "West Drayton, Middlesex",
            ),
        )

    def test_birth_date(self):
        self.source.update(
            {
                "birth": {
                    "date": {"value": "1897"},
                }
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.birth_date, "1897")
        self.assertEqual(self.record.record_creators_date, "1897")

    def test_death_date(self):
        self.source.update(
            {
                "death": {
                    "date": {"value": "1981"},
                }
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.death_date, "1981")
        self.assertEqual(self.record.record_creators_date, "1981")

    def test_start_date(self):
        self.source.update(
            {
                "start": {
                    "date": [{"value": "1935"}],
                }
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.start_date, "1935")
        self.assertEqual(self.record.record_creators_date, "1935")

    def test_end_date(self):
        self.source.update(
            {
                "end": {
                    "date": [{"value": "1974"}],
                }
            }
        )
        self.record = Record(self.source)

        self.assertEqual(self.record.end_date, "1974")
        self.assertEqual(self.record.record_creators_date, "1974")

    def test_record_creators_date_with_birth_death_dates(self):
        self.source.update(
            {
                "birth": {
                    "date": {"value": "1897"},
                },
                "death": {
                    "date": {"value": "1981"},
                },
            }
        )

        self.record = Record(self.source)

        self.assertEqual(self.record.record_creators_date, "1897-1981")

    def test_record_creators_date_with_start_end_dates(self):
        self.source.update(
            {
                "birth": {
                    "date": {"value": "1897"},
                },
                "death": {
                    "date": {"value": "1981"},
                },
                "start": {
                    "date": [{"value": "1935"}],
                },
                "end": {
                    "date": [{"value": "1974"}],
                },
            }
        )

        self.record = Record(self.source)

        self.assertEqual(self.record.record_creators_date, "1897-1981; 1935-1974")

    def test_record_creators_date_with_all_dates(self):
        self.source.update(
            {
                "start": {
                    "date": [{"value": "1935"}],
                },
                "end": {
                    "date": [{"value": "1974"}],
                },
            }
        )

        self.record = Record(self.source)

        self.assertEqual(self.record.record_creators_date, "1935-1974")

    def test_name_authority_reference(self):
        self.source.update(
            {
                "identifier": [
                    {
                        "name_authority_reference": "GB/NNAF/P163769",
                        "type": "name authority reference",
                        "value": "GB/NNAF/P163769",
                    },
                ],
            }
        )

        self.record = Record(self.source)

        self.assertEqual(self.record.name_authority_reference, "GB/NNAF/P163769")

    def test_former_name_authority_reference(self):
        self.source.update(
            {
                "identifier": [
                    {
                        "former_name_authority_reference": "GB/NNAF/P16782",
                        "type": "former name authority reference",
                        "value": "GB/NNAF/P16782",
                    },
                ],
            }
        )

        self.record = Record(self.source)

        self.assertEqual(self.record.former_name_authority_reference, "GB/NNAF/P16782")
