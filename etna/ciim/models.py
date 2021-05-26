from dataclasses import dataclass

from django.apps import apps
from django.conf import settings
from django.utils.html import strip_tags

from .client import KongClient
from .exceptions import DoesNotExist, MultipleObjectsReturned, InvalidIAIDMatch
from .utils import value_from_dictionary_in_list


def translate_result(result):
    data = {}

    source = result["_source"]
    identifier = source.get("identifier")

    data["iaid"] = value_from_dictionary_in_list(identifier, "iaid")
    data["reference_number"] = value_from_dictionary_in_list(
        identifier, "reference_number"
    )

    if title := source.get("title"):
        data["title"] = title[0]["value"]

    if access := source.get("access"):
        data["closure_status"] = access.get("conditions")

    if origination := source.get("@origination"):
        try:
            data["created_by"] = origination["creator"][0]["name"][0]["value"]
        except KeyError:
            ...
        data["date_start"] = origination["date"]["earliest"]["from"]
        data["date_end"] = origination["date"]["latest"]["to"]
        data["date_range"] = origination["date"]["value"]

    if description := source.get("description"):
        data["description"] = description[0]["value"]

    if legal := source.get("legal"):
        data["legal_status"] = legal["status"]

    return data


class SearchManager:
    def __init__(self, model):
        self.model = model
        self.client = KongClient(settings.KONG_CLIENT_BASE_URL)

    def filter(self, **kwargs):
        response = self.client.search(**kwargs)

        results = response["hits"]["hits"]

        data = [translate_result(r) for r in results]

        # TODO this returns one item!
        return apps.get_model(self.model)(**data)

    def get(self, iaid=None):
        response = self.client.search(term=iaid)

        results = response["hits"]["hits"]
        results_count = response['hits']['total']['value']
        if results_count == 0:
            raise DoesNotExist
        if results_count > 1:
            raise MultipleObjectsReturned

        result = results[0]
        if result["_source"]["@admin"]["id"] != iaid:
            raise InvalidIAIDMatch

        data = translate_result(result)

        return apps.get_model(self.model)(**data)
