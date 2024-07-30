import json

from typing import Any, Dict, Optional


def create_record(
    group="tna",
    iaid="C0000000",
    ciim_id="swop-0000000",
    admin_source="mongo",
    reference_number="ADM 223/3",
    summary_title="Summary Title",
    description="description",
    earliest="1900",
    latest="2100",
    hierarchy=None,
    related=None,
    source_values: Optional[Dict[str, Any]] = None,
    add_template_details: Optional[Dict[str, Any]] = None,
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
    #     "@hierarchy": [hierarchy],
    #     "summary": {
    #         "title": summary_title,
    #     },
    #     "related": related,
    #     "description": [{"value": description}],
    #     "legal": {"status": "Open"},
    # }

    details_kv = {}
    if group == "community":
        iaid = reference_number = ""
        details_kv.update(ciimId=ciim_id, group=group)
    else:
        details_kv.update(iaid=iaid)

    if reference_number:
        details_kv.update(referenceNumber=reference_number)
    if description:
        details_kv.update(description=description)

    if add_template_details:
        for key, value in add_template_details.items():
            details_kv.update({key: value})

    record = {"@template": {"details": details_kv}}

    # note keys used in existing source will be overridden
    if source_values:
        for source_key_value in source_values:
            for key, value in source_key_value.items():
                record[key] = value

    return record


def create_response(record={}, status_code=None):
    """ """
    if status_code == 400:
        return {
            "status": "Bad Request",
            "status_code": 400,
            "message": "Required request parameter 'id' for method parameter type String is not present",
        }

    if status_code == 404:
        return {
            "status": "Not Found",
            "status_code": 404,
            "message": "No data found with id 'VALUEDOESNOTEXIST'",
        }

    return {
        "data": record,
        "aggregations": [],
        "stats": {
            "total": 1,
        },
    }


def create_search_response(
    records=None, aggregations=None, buckets=None, total_count=None
):
    if not records:
        records = []
    if not aggregations:
        aggregations = []
    if not buckets:
        buckets = []
    if not total_count:
        total_count = len(records)

    return {
        "data": records,
        "aggregations": aggregations,
        "buckets": buckets,
        "stats": {
            "total": total_count,
        },
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
