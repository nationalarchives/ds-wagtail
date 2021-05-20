from dataclasses import dataclass

from django.apps import apps
from django.conf import settings
from django.utils.html import strip_tags

from .client import KongClient
from .exceptions import DoesNotExist, MultipleObjectsReturned, InvalidCatalogueIdMatch
from .utils import value_from_dictionary_in_list


def translate_result(result):
    data = {}

    source = result["_source"]

    if identifier := source.get("identifier"):
        data["catalogue_id"] = value_from_dictionary_in_list(identifier, "iaid")
        data["reference_number"] = value_from_dictionary_in_list(
            identifier, "reference_number"
        )

    if title := source.get("title"):
        data["title"] = title[0]["value"]

    # rename catalogue_id to iaid
    # parse out relationships
    data['closure_status'] = result['_source']['access']['conditions']
    data["created_by"] = result['_source']['origination']['creator'][0]['name'][0]['value']
    # Strip SCOPE AND CONTENT, Resolve linkes
    data["description"] = source["description"][0]["value"]
    data["date_start"] = source["origination"]["date"]["earliest"]
    data["date_end"] = source["origination"]["date"]["latest"]
    data["date_range"] = source["origination"]["date"]["value"]
    data["legal_status"] = source["legal"]["status"]

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

    def get(self, catalogue_id=None):
        response = self.client.search(term=catalogue_id)

        results = response["hits"]["hits"]
        results_count = response['hits']['total']['value']
        if results_count == 0:
            raise DoesNotExist
        if results_count > 1:
            raise MultipleObjectsReturned

        result = results[0]
        if result["_source"]["@admin"]["id"] != catalogue_id:
            raise InvalidCatalogueIdMatch

        data = translate_result(result)

        return apps.get_model(self.model)(**data)
