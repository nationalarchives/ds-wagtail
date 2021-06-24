import json

from django.conf import settings

import requests

from .exceptions import InvalidResponse, KubernetesError, KongError, ConnectionError
from .utils import pluck


def mock_response_from_file(filename, **kwargs):

    # Mimic Kong's behaviour by searching multiple fields with the 'term' param
    term = (
        kwargs.get("iaid") or kwargs.get("reference_number") or kwargs.get("term") or ""
    )
    # Convert to lower case to match Kong's case insensitive matching on IDs
    term = term.lower()

    with open(filename) as f:
        response = json.loads(f.read())
        response["hits"]["hits"] = [
            r
            for r in response["hits"]["hits"]
            if r["_source"]["@admin"]["id"].lower() == term
            or pluck(
                r["_source"]["identifier"],
                accessor=lambda i: i["reference_number"],
                default="",
            ).lower()
            == term
            or term in r["_source"]["description"][0]["value"].lower()
            or term in r["_source"]["@summary"]["title"].lower()
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

        try:
            response = requests.get(self.base_url + "/fetch", params=kwargs, timeout=5)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e

        if not response.ok:
            raise InvalidResponse("Invalid response")

        json = response.json()

        if "message" in json:
            raise KubernetesError(json["message"])

        if "error" in json:
            raise KongError(f"Kong returned status {json['status']}")

        return json

    def search(self, **kwargs):

        if term := (
            kwargs.pop("iaid", None)
            or kwargs.pop("reference_number", None)
            or kwargs.pop("term", None)
            or ""
        ):
            kwargs["term"] = term

        if settings.KONG_CLIENT_TEST_MODE:
            return mock_response_from_file(settings.KONG_CLIENT_TEST_FILENAME, **kwargs)

        # from isn'ca valid kwargs
        kwargs["from"] = kwargs.pop("start", 0)
        kwargs["pretty"] = "true" if kwargs.pop("pretty", False) else "false"

        try:
            response = requests.get(self.base_url + "/search", params=kwargs, timeout=5)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e

        if not response.ok:
            raise InvalidResponse("Invalid response.")

        json = response.json()

        if "message" in json:
            raise KubernetesError(json["message"])

        if "error" in json:
            raise KongError(f"Kong returned status {json['status']}")

        return json
