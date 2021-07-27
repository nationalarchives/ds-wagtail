def create_record(
    iaid="C0000000",
    reference_number="ADM 223/3",
    title="Title",
    description="description",
):
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
            "description": [{"value": description}],
            "legal": {"status": "Open"},
        }
    }


def create_response(records=None, total_count=None):
    """Create a sample Elasticsearch response for provided records. 

    If testing pagination or batch fetches, the total count can be optionally
    modified.
    """
    if not records:
        records = []

    if not total_count:
        total_count = len(records)

    return {
        "hits": {
            "total": {"value": total_count, "relation": "eq"},
            "hits": [r for r in records],
        }
    }
