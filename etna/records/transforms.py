from ..ciim.utils import pluck


def transform_image_result(result):
    """Fetch data from an Elasticsearch response to pass to Image.__init__"""

    data = {}

    data["thumbnail_location"] = pluck(
        result["_source"],
        accessor=lambda i: i["processed"]["preview"]["location"],
    )
    data["location"] = result["_source"]["processed"]["original"]["location"]
    data["sort"] = result["_source"]["sort"]

    return data
