from django.core.exceptions import PermissionDenied
from django.http import Http404
from requests import (
    HTTPError,
    JSONDecodeError,
    RequestException,
    Timeout,
    TooManyRedirects,
    get,
)


class APIClientError(Exception):
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response


class JSONAPIClient:
    """
    A client for interacting with a JSON API, which can be extended for specific APIs.
    """

    def __init__(self, api_url: str, params: dict = {}):
        self.api_url: str = api_url
        self.params: dict = params

    def add_parameter(self, key: str, value: str | int | bool):
        self.params[key] = value

    def add_parameters(self, params: dict):
        self.params |= params

    def get(self, path: str = "/", headers: dict = None) -> dict:
        url = f"{self.api_url}/{path.lstrip("/")}"

        if headers is None:
            headers = {
                "Cache-Control": "no-cache",
                "Accept": "application/json",
            }

        try:
            response = get(
                url,
                params=self.params,
                headers=headers,
            )
            response.raise_for_status()
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            raise RequestException(str(e))
        except HTTPError:
            if response.status_code == 400:
                raise APIClientError("Bad request", response=response)
            elif response.status_code == 401:
                raise PermissionDenied("Unauthorized request")
            elif response.status_code == 403:
                raise PermissionDenied("Forbidden")
            elif response.status_code == 404:
                raise Http404("Resource not found")
            else:
                raise Exception(
                    f"Request failed with status code {response.status_code}"
                )
        except Exception:
            raise Exception("Request failed")
        try:
            return response.json()
        except JSONDecodeError:
            raise Exception("Non-JSON response provided")
