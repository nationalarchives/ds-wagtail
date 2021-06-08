from django.apps import apps
from django.conf import settings
from django.utils.functional import cached_property

from .client import KongClient
from .exceptions import DoesNotExist, MultipleObjectsReturned
from .utils import (
    value_from_dictionary_in_list,
    format_description_markup,
    translate_result,
)


class SearchManager:
    def __init__(self, model):
        self.model = model

    @cached_property
    def client(self):
        """Lazy-load client to allow tests to overwrite base url."""
        return KongClient(settings.KONG_CLIENT_BASE_URL)

    def filter(self, **kwargs):
        response = self.client.search(**kwargs)

        results = response["hits"]["hits"]

        translated_results = [translate_result(r) for r in results]

        return [apps.get_model(self.model)(**r) for r in translated_results]

    def get(self, iaid=None, reference_number=None):
        response = self.client.fetch(iaid=iaid, reference_number=reference_number)

        results = response["hits"]["hits"]
        results_count = response["hits"]["total"]["value"]
        if results_count == 0:
            raise DoesNotExist
        if results_count > 1:
            raise MultipleObjectsReturned

        result = results[0]

        data = translate_result(result)

        return apps.get_model(self.model)(**data)
