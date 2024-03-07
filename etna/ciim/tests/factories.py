import json

from collections.abc import Mapping
from typing import Any, Dict, Optional

from django.conf import settings


def create_record(
    iaid="C0000000",
    admin_source="mongo",
    reference_number="ADM 223/3",
    summary_title="Summary Title",
    description="description",
    earliest="1900",
    latest="2100",
    is_digitised=False,
    media_reference_id="0f183772-6fa7-4fb4-b608-412cf6fa8204",
    hierarchy=None,
    related=None,
    source_values: Optional[Dict[str, Any]] = None,
):
    """Return a sample response for a record.

    Useful for tidying up tests where response needs to be mocked

    source_values: use to setup multiple key-values in _source attribute
    Ex: source_values=[{"key1": <value1>, "key2": <value2>}]

    Note: keys used in existing source will be overridden
    """
    # TODO:Rosetta
    # if not hierarchy:
    #     hierarchy = []

    # if not related:
    #     related = []

    # source = {
    #     "@admin": {
    #         "id": iaid,
    #         "source": admin_source,
    #     },
    #     "access": {"conditions": "open"},
    #     "identifier": [
    #         {"iaid": iaid},
    #         {"reference_number": reference_number},
    #     ],
    #     "origination": {
    #         "creator": [{"name": [{"value": "test"}]}],
    #         "date": {
    #             "earliest": {"from": earliest},
    #             "latest": {"to": latest},
    #             "value": f"{earliest}-{latest}",
    #         },
    #     },
    #     "digitised": is_digitised,
    #     "@hierarchy": [hierarchy],
    #     "summary": {
    #         "title": summary_title,
    #     },
    #     "multimedia": [
    #         {
    #             "@entity": "reference",
    #             "@admin": {
    #                 "id": media_reference_id,
    #             },
    #         }
    #     ],
    #     "related": related,
    #     "description": [{"value": description}],
    #     "legal": {"status": "Open"},
    # }

    details_kv = {}
    details_kv.update(iaid=iaid)
    if reference_number:
        details_kv.update(reference_number=reference_number)
    if description:
        details_kv.update(description=description)
    detail = {"id": iaid, "detail": {"@template": {"details": details_kv}}}

    # note keys used in existing source will be overridden
    if source_values:
        for source_key_value in source_values:
            for key, value in source_key_value.items():
                detail[key] = value

    # return {"_source": source}  # TODO:Rosetta
    return detail


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
    if records is None:
        records = []

    if aggregations is None:
        aggregations = {}

    if total_count is None:
        total_count = len(records)

    return {
        "metadata": [r for r in records],
        "stats": {
            "total": {"value": total_count, "relation": "eq"},
        },
        "aggregations": aggregations,
    }


def create_iiif_manifest_response(record_id: str) -> Mapping[str, Any]:
    server = settings.CLIENT_IIIF_MANIFEST_BASE_URL
    return {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": f"{server}/manifest/{record_id}",
        "type": "Manifest",
        "label": {"en": [f"Test label for {record_id}"]},
        "summary": {
            "en": [
                f'<span class="wrapper"><span class="scopecontent"><p>Text description <a class="extref" href="{record_id}">{record_id}</a>.</p></span></span>'
            ]
        },
        "items": [
            {
                "id": f"{server}/manifest/{record_id}/items/0",
                "type": "Canvas",
                "height": 200,
                "width": 100,
                "items": [
                    {
                        "id": f"{server}/manifest/{record_id}/items/0/items/0",
                        "type": "AnnotationPage",
                        "items": [
                            {
                                "id": f"{server}/manifest/{record_id}/items/0/items/0/items/0",
                                "type": "Annotation",
                                "body": {
                                    "id": f"{server}/testlocation/{record_id}/full/max/0/default.jpg",
                                    "type": "Image",
                                    "service": [
                                        {
                                            "id": f"{server}/testlocation/{record_id}/info.json",
                                            "type": "ImageService3",
                                            "profile": "level1",
                                        }
                                    ],
                                    "height": 200,
                                    "width": 100,
                                },
                                "motivation": "painting",
                                "target": f"{server}/manifest/{record_id}/items/0",
                            }
                        ],
                    }
                ],
            },
        ],
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
