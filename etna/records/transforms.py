from ..ciim.utils import format_description_markup, pluck, find


def transform_record_page_result(result):
    """Fetch data from an Elasticsearch response to pass to RecordPage.__init__"""

    data = {}

    source = result["_source"]
    identifier = source.get("identifier")
    summary = source.get("@summary")

    data["iaid"] = source["@admin"]["id"]
    data["reference_number"] = pluck(
        identifier, accessor=lambda i: i.get("reference_number")
    )
    data["title"] = summary.get("title")

    if access := source.get("access"):
        data["closure_status"] = access.get("conditions")

    if origination := source.get("@origination"):
        data["created_by"] = pluck(
            origination, accessor=lambda i: i["creator"][0]["name"][0]["value"]
        )
        if origination["date"]["value"] != "undated":
            data["date_start"] = origination["date"]["earliest"]["from"]
            data["date_end"] = origination["date"]["latest"]["to"]
            data["date_range"] = origination["date"]["value"]

    if description := source.get("description"):
        data["description"] = format_description_markup(description[0]["value"])

    if arrangement := source.get("arrangement"):
        data["arrangement"] = format_description_markup(arrangement["value"])

    if legal := source.get("legal"):
        data["legal_status"] = legal["status"]

    if repository := source.get("repository"):
        data["held_by"] = repository["name"]["value"]

    data["is_digitised"] = source.get("digitised", False)

    if parent := find(
        source.get("association"),
        predicate=lambda i: i["@link"]["role"][0]["value"] == "parent",
    ):
        data["parent"] = {
            "iaid": parent["@admin"]["id"],
            "title": parent["@summary"]["title"],
        }

    if hierarchy := source.get("hierarchy"):
        data["hierarchy"] = [
            {
                "reference_number": i["identifier"][0]["reference_number"],
                "title": i["@summary"]["title"],
            }
            for i in hierarchy[0]
        ]

    if availability := source.get("availability"):
        if access := availability.get("access"):
            data["availablility_access_display_label"] = access["display"]["label"][
                "value"
            ]
            data["availablility_access_closure_label"] = pluck(
                access["closure"], accessor=lambda i: i["display"]["label"]["value"]
            )
        if delivery := availability.get("delivery"):
            data["availablility_delivery_condition"] = delivery["condition"]["value"]
            data["availablility_delivery_surrogates"] = delivery.get("surrogate")

    data["media_reference_id"] = pluck(
        source.get("multimedia"), accessor=lambda i: i["@admin"]["id"]
    )

    return data


def transform_image_result(result):
    """Fetch data from an Elasticsearch response to pass to Image.__init__"""

    data = {}

    data["location"] = result["_source"]["processed"]["original"]["location"]

    return data
