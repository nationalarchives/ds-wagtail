import json
import logging

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)
"""Although this is not a ciim specific class, use the predefined API exceptions for consistency """
from etna.ciim.exceptions import (
    ClientAPIBadRequestError,
    ClientAPICommunicationError,
    ClientAPIInternalServerError,
    ClientAPIServiceUnavailableError,
    DoesNotExist,
    MultipleObjectsReturned,
)

import requests

class DeliveryOptionsAPI:
    """Client used to Fetch and validate data from Client API."""

    http_error_classes = {
        400: ClientAPIBadRequestError,
        500: ClientAPIInternalServerError,
        503: ClientAPIServiceUnavailableError,
    }
    default_http_error_class = ClientAPICommunicationError

    def __init__(
        self,
        base_url: str,
        timeout: int = 5,
    ):
        self.base_url: str = base_url
        self.session = requests.Session()
        self.timeout = timeout

    def fetch(
        self,
        *,
        iaid: Optional[str] = None,
        id: Optional[str] = None,
    ) -> dict:
        """Make request and return response for Client API's endpoint.

        Used to fetch a single item by its identifier.

        Keyword arguments:

        iaid:
            Return match on Information Asset Identifier - iaid (or similar primary identifier)
        id:
            Generic identifier. Matches on references_number or iaid
        """
        params = {
            "iaid": iaid,
            "id": id,
        }

        # Get HTTP response from the API
        response = self.make_request(f"{self.base_url}", params=params)

        # Convert the HTTP response to a Python dict
        response_data = response.json()

        if not response_data:
            raise DoesNotExist
        if len(response_data) > 1:
            raise MultipleObjectsReturned
        return response_data

    def prepare_request_params(
        self, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Process parameters before passing to Client API.

        Remove empty values to make logged requests cleaner.
        """
        if not data:
            return {}

        return {k: v for k, v in data.items() if v is not None}

    def make_request(
        self, url: str, params: Optional[dict[str, Any]] = None
    ) -> requests.Response:
        
        """Make request to Client API."""
        params = self.prepare_request_params(params)
        response = self.session.get(url, params=params, timeout=self.timeout)
        self._raise_for_status(response)
        return response

    def _raise_for_status(self, response: requests.Response) -> None:
        """Raise custom error for any requests.HTTPError raised for a request.

        ClientAPIErrors include response body in message to aide debugging.
        """
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_class = self.http_error_classes.get(
                e.response.status_code, self.default_http_error_class
            )

            try:
                response_body = json.dumps(response.json(), indent=4)
            except json.JSONDecodeError:
                response_body = response.text

            raise error_class(
                f"Response body: {response_body}", response=response
            ) from e
