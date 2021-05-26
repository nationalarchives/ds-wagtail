import json

from django.conf import settings

import requests

from .exceptions import InvalidResponse, KubernetesError, KongError
from .utils import value_from_dictionary_in_list


def mock_response_from_file(filename, **kwargs):

    # Mimic Kong's behaviour by searching multiple fields with the 'term' param
    term = kwargs.get('iaid') or kwargs.get('reference_number') or kwargs.get('term')

    with open(filename) as f:
        response = json.loads(f.read())
        response["hits"]["hits"] = [
            r
            for r in response["hits"]["hits"]
            if value_from_dictionary_in_list(r["_source"]["identifier"], "iaid") == term
            or value_from_dictionary_in_list(
                r["_source"]["identifier"], "reference_number"
            )
            == term
        ]
        response["hits"]["total"]["value"] = len(response["hits"]["hits"])
        return response


class KongClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch(self, **kwargs):
        if settings.KONG_CLIENT_TEST_MODE:
            return mock_response_from_file(settings.KONG_CLIENT_TEST_FILENAME, **kwargs)

        kwargs["ref"] = kwargs.pop("reference_number", None)
        kwargs["from"] = kwargs.pop("start", 0)
        kwargs["pretty"] = "true" if kwargs.pop("pretty", False) else "false"

        response = requests.get(self.base_url + "/fetch", params=kwargs, timeout=5)

        if not response.ok:
            raise InvalidResponse("Invalid response.")

        json = response.json()

        if "message" in json:
            raise KubernetesError(json["message"])

        if "error" in json:
            raise KongError(f"Kong returned status {json['status']}")

        return json

    def search(self, **kwargs):

        if settings.KONG_CLIENT_TEST_MODE:
            return mock_response_from_file(settings.KONG_CLIENT_TEST_FILENAME, **kwargs)

        # from isn't a valid kwargs
        kwargs["from"] = kwargs.pop("start", 0)
        kwargs["pretty"] = "true" if kwargs.pop("pretty", False) else "false"

        response = requests.get(self.base_url + "/search", params=kwargs, timeout=5)

        if not response.ok:
            raise InvalidResponse("Invalid response.")

        json = response.json()

        if "message" in json:
            raise KubernetesError(json["message"])

        if "error" in json:
            raise KongError(f"Kong returned status {json['status']}")

        return json
