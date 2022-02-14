import logging

import requests

from .exceptions import ConnectionError, InvalidResponse, KongError, KubernetesError

logger = logging.getLogger(__name__)


class KongClient:
    def __init__(self, base_url, api_key, verify_certificates=True):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"apikey": api_key})
        self.session.verify = verify_certificates

    def fetch(self, **kwargs):
        kwargs["ref"] = kwargs.pop("reference_number", None)
        kwargs["from"] = kwargs.pop("start", 0)
        kwargs["expand"] = "true" if kwargs.pop("expand", False) else "false"

        try:
            response = self.session.get(
                self.base_url + "/data/fetch", params=kwargs, timeout=5
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e

        if not response.ok:
            raise InvalidResponse("Invalid response")

        json = response.json()

        logger.debug(f"Response from Kong: {json}")

        if "message" in json:
            raise KubernetesError(json["message"])

        if "error" in json:
            raise KongError(f"Kong returned status {json['status']}")

        return json

    def search(self, **kwargs):

        if term := (
            kwargs.pop("iaid", None)
            or kwargs.pop("reference_number", None)
            or kwargs.pop("keyword", None)
            or ""
        ):
            kwargs["keyword"] = term

        # In Python 'from' cannot be a kwargs. Map 'start' to 'from' before making request
        kwargs["from"] = kwargs.pop("start", 0)

        try:
            response = self.session.get(
                self.base_url + "/data/search", params=kwargs, timeout=5
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e

        if not response.ok:
            raise InvalidResponse("Invalid response.", json=response.json())

        json = response.json()

        logger.debug(f"Response from Kong: {json}")

        if "message" in json:
            raise KubernetesError(json["message"])

        if "error" in json:
            raise KongError(f"Kong returned status {json['status']}")

        return json

    def media(self, location=None):
        try:
            return self.session.get(
                f"{self.base_url}/media/{location}", stream=True, timeout=5
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e
