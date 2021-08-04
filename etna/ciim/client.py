import json

from django.conf import settings

import requests

from .exceptions import InvalidResponse, KubernetesError, KongError, ConnectionError
from .utils import pluck

import logging
logger = logging.getLogger(__name__)


def mock_response_from_file(filename, **kwargs):

    def match(record, term):
        """Emulate Kong's search.

        If data is missing from response, skip and try the next comparison.

        Refactor as soon as possible (potentially using 3.10's Structural
        Pattern Matching)
        """
        try:
            if success := record["_source"]["@admin"]["id"].lower() == term:
                return success
        except KeyError:
            # Try next comparison
            ...

        try:
            if success := pluck(
                record["_source"]["identifier"],
                accessor=lambda i: i["reference_number"],
                default="",
            ).lower() == term:
                return success
        except KeyError:
            # Try next comparison
            ...

        try:
            if success := term in record["_source"]["description"][0]["value"].lower():
                return success
        except (KeyError, IndexError):
            # Try next comparison
            ...

        try:
            if success := term in record["_source"]["@summary"]["title"].lower():
                return success
        except KeyError:
            # Try next comparison
            ...

        return False


    # Mimic Kong's behaviour by searching multiple fields with the 'term' param
    term = (
        kwargs.get("iaid") or kwargs.get("reference_number") or kwargs.get("term") or ""
    )
    # Convert to lower case to match Kong's case insensitive matching on IDs
    term = term.lower()

    with open(filename) as f:
        response = json.loads(f.read())
        response["hits"]["hits"] = [r for r in response["hits"]["hits"] if match(r, term)]
        response["hits"]["total"]["value"] = len(response["hits"]["hits"])
        return response


class KongClient:
    def __init__(self, base_url, api_key, test_mode=False, test_file_path=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'apikey': api_key})
        self.test_mode = test_mode
        self.test_file_path = test_file_path

    def fetch(self, **kwargs):
        if self.test_mode:
            return mock_response_from_file(self.test_file_path, **kwargs)

        kwargs["ref"] = kwargs.pop("reference_number", None)
        kwargs["from"] = kwargs.pop("start", 0)
        kwargs["pretty"] = "true" if kwargs.pop("pretty", False) else "false"

        try:
            response = self.session.get(self.base_url + "/fetch", params=kwargs, timeout=5)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e

        if not response.ok:
            raise InvalidResponse("Invalid response")

        json = response.json()

        logger.debug(f'Response from Kong: {json}')

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

        if self.test_mode:
            return mock_response_from_file(self.test_file_path, **kwargs)

        # In Python 'from' cannot be a kwargs. Map 'start' to 'from' before making request
        kwargs["from"] = kwargs.pop("start", 0)
        kwargs["pretty"] = "true" if kwargs.pop("pretty", False) else "false"

        try:
            response = self.session.get(self.base_url + "/search", params=kwargs, timeout=5)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e

        if not response.ok:
            raise InvalidResponse("Invalid response.", json=response.json())

        json = response.json()

        logger.debug(f'Response from Kong: {json}')

        if "message" in json:
            raise KubernetesError(json["message"])

        if "error" in json:
            raise KongError(f"Kong returned status {json['status']}")

        return json

    def media(self, location=None):
        try:
            return self.session.get(f"{self.base_url}/media/{location}", stream=True, timeout=5)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e
