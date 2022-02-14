from ..ciim.utils import find_all, format_description_markup, pluck
from ..ciim.exceptions import InValidResult


def transform_record_result(result):
    """Fetch data from an Elasticsearch response to pass to Record.__init__"""
    data = {}
    if not result:
        raise InValidResult
    if "_source" not in result:
        raise InValidResult

    source = result["_source"]
    identifier = source.get("identifier")
    summary = source.get("summary")

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
        data["origination_date"] = pluck(
            origination, accessor=lambda i: i["date"]["value"]
        )

    if description := source.get("description"):
        data["description"] = format_description_markup(description[0]["value"])

    if arrangement := source.get("arrangement"):
        data["arrangement"] = format_description_markup(arrangement["value"])

    if legal := source.get("legal"):
        data["legal_status"] = legal["status"]

    if repository := source.get("repository"):
        data["held_by"] = repository["name"]["value"]

    data["is_digitised"] = source.get("digitised", False)

    if parent := source.get("parent"):
        data["parent"] = {
            "iaid": pluck(parent, accessor=lambda i: i["@admin"]["id"]),
            "reference_number": pluck(
                parent,
                accessor=lambda i: i["identifier"][0]["reference_number"],
            ),
            "title": pluck(parent, accessor=lambda i: i["summary"]["title"]),
        }

    if hierarchy := source.get("hierarchy"):
        data["hierarchy"] = [
            {
                "reference_number": i["identifier"][0]["reference_number"],
                "title": i["summary"]["title"],
            }
            for i in hierarchy[0]
            if "identifier" in i
        ]

    if availability := source.get("availability"):
        if delivery := availability.get("delivery"):
            data["availability_delivery_condition"] = delivery["condition"]["value"]
            data["availability_delivery_surrogates"] = delivery.get("surrogate")

    if topics := source.get("topic"):
        data["topics"] = [
            {
                "title": i["summary"]["title"],
            }
            for i in topics
        ]

    if related := source.get("related"):
        related_records = find_all(
            related,
            predicate=lambda i: i["@link"]["relationship"]["value"] == "related",
        )
        data["related_records"] = [
            {
                "title": i["summary"]["title"],
                "iaid": i["@admin"]["id"],
            }
            for i in related_records
        ]

        related_articles = find_all(
            related, predicate=lambda i: i["@admin"]["source"] == "wagtail-es"
        )
        data["related_articles"] = [
            {"title": i["summary"]["title"], "url": i["source"]["location"]}
            for i in related_articles
            if 'summary' in i
        ]

    data["media_reference_id"] = pluck(
        source.get("multimedia"), accessor=lambda i: i["@admin"]["id"]
    )

    if next_record := source.get("@next"):
        data["next_record"] = {"iaid": next_record["@admin"]["id"]}

    if previous_record := source.get("@previous"):
        data["previous_record"] = {"iaid": previous_record["@admin"]["id"]}

    return data


def transform_image_result(result):
    """Fetch data from an Elasticsearch response to pass to Image.__init__"""

    data = {}

    data["thumbnail_location"] = pluck(
        result["_source"], accessor=lambda i: i["processed"]["preview"]["location"]
    )
    data["location"] = result["_source"]["processed"]["original"]["location"]
    data["sort"] = result["_source"]["sort"]

    return data
