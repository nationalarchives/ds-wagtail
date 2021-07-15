def create_record(iaid="C0000000", reference_number="ADM 223/3", title="Title"):
    """Return a sample response for a record.

    Useful for tidying up tests where response needs to be mocked
    """
    return {
        "_source": {
            "@admin": {
                "id": iaid,
            },
            "access": {"conditions": "open"},
            "identifier": [
                {"iaid": iaid},
                {"reference_number": reference_number},
            ],
            "origination": {
                "creator": [{"name": [{"value": "test"}]}],
                "date": {
                    "earliest": "1900",
                    "latest": "2100",
                    "value": "1900-2100",
                },
            },
            "@summary": {
                "title": title,
            },
            "description": [{"value": "description"}],
            "legal": {"status": "Open"},
        }
    }


def create_response(records=None):
    """Create a sample Elasticsearch response for provided records.  """
    if not records:
        records = []

    return {
        "hits": {
            "total": {"value": len(records), "relation": "eq"},
            "hits": [r for r in records],
        }
    }
