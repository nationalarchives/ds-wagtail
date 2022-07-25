import json


def create_record(
    iaid="C0000000",
    source="mongo",
    reference_number="ADM 223/3",
    title="Title",
    description="description",
    earliest="1900",
    latest="2100",
    is_digitised=False,
    media_reference_id="0f183772-6fa7-4fb4-b608-412cf6fa8204",
    hierarchy=None,
    related=None,
):
    if not hierarchy:
        hierarchy = []

    if not related:
        related = []

    """Return a sample response for a record.

    Useful for tidying up tests where response needs to be mocked
    """
    return {
        "_source": {
            "@admin": {
                "id": iaid,
                "source": source,
            },
            "access": {"conditions": "open"},
            "identifier": [
                {"iaid": iaid},
                {"reference_number": reference_number},
            ],
            "origination": {
                "creator": [{"name": [{"value": "test"}]}],
                "date": {
                    "earliest": {"from": earliest},
                    "latest": {"to": latest},
                    "value": f"{earliest}-{latest}",
                },
            },
            "digitised": is_digitised,
            "@hierarchy": [hierarchy],
            "summary": {
                "title": title,
            },
            "multimedia": [
                {
                    "@entity": "reference",
                    "@admin": {
                        "id": media_reference_id,
                    },
                }
            ],
            "related": related,
            "description": [{"value": description}],
            "legal": {"status": "Open"},
        }
    }


def create_media(
    location="66/KV/2/444a48ad-f9eb-4f40-b159-396dc7fa6875.jpg",
    thumbnail_location="66/COPY/KV/2/444a48ad-f9eb-4f40-b159-396dc7fa6875.jpg",
    sort="01",
):
    return {
        "_source": {
            "processed": {
                "original": {
                    "location": location,
                    "public": True,
                    "resizable": True,
                    "@type": "image",
                },
                "preview": {
                    "location": thumbnail_location,
                    "public": True,
                    "resizable": True,
                    "@type": "image",
                },
            },
            "sort": sort,
        }
    }


def create_response(records=None, aggregations=None, total_count=None):
    """Create a sample Elasticsearch response for provided records.

    If testing pagination or batch fetches, the total count can be optionally
    modified.
    """
    if not records:
        records = []

    if not aggregations:
        aggregations = {}

    if not total_count:
        total_count = len(records)

    return {
        "hits": {
            "total": {"value": total_count, "relation": "eq"},
            "hits": [r for r in records],
        },
        "aggregations": aggregations,
    }


def create_search_response(records=None, aggregations=None, total_count=None):
    if not records:
        records = []

    if not aggregations:
        aggregations = {}

    if not total_count:
        total_count = len(records)

    return {
        "responses": [
            create_response(aggregations=aggregations, total_count=total_count),
            create_response(records=records, total_count=total_count),
        ]
    }


def paginate_records_callback(records, request):
    """Responses callback to simulate paginating through results.

    Page through records, responding with a all or a single record if
    requested or nothing if requested record doesn't exist."""
    start = int(request.params.get("from", 0))
    size = request.params.get(
        "size",
    )
    stop = start + int(size) if size else None

    try:
        response_records = records[start:stop]
    except TypeError:
        response_records = records[start:]
    except IndexError:
        response_records = []

    return (
        200,
        {},
        json.dumps(create_response(records=response_records, total_count=len(records))),
    )
