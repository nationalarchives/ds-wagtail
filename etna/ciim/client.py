from django.conf import settings

from etna.core.api import JSONAPIClient
from sentry_sdk import capture_message

class CIIMClient(JSONAPIClient):
    """
    Client for interacting with the CIIM API.
    """

    def __init__(self, api_url: str = f"{settings.CLIENT_BASE_URL}", params: dict = {}):
        self.api_url: str = api_url
        self.params: dict = params

    def get_record_instance(self, path: str = "/get") -> dict:
        """
        Get a single record instance from the CIIM API.
        """
        try:
            response = self.get(path=path, headers={})
        except Exception as e:
            capture_message(f"CIIMClient.get_record_instance: {e}", level="error")
            response = {"data": []}

        try:
            result = response.get("data", [])[0].get("@template", {}).get("details", {})
        except IndexError:
            result = {"referenceNumber": None, "summaryTitle": "CLIENT ERROR", "iaid": self.params.get("id")}
        return result

    def get_record_list(self, path: str = "/search") -> tuple:
        """
        Get a list of records from the CIIM API.
        """
        try:
            response = self.get(path=path, headers={})
        except Exception as e:
            capture_message(f"CIIMClient.get_record_list: {e}", level="error")
            response = {"data": []}

        results = response.get("data", [])
        total = response.get("stats", {}).get("total", 0)
        return results, total

    def get_serialized_record(self) -> dict:
        """
        Get a standardised serialized record from the CIIM API for the Wagtail API.
        """
        instance = self.get_record_instance()

        if instance:
            return {
                "title": instance.get("summaryTitle", None),
                "iaid": instance.get("iaid", None),
                "reference_number": instance.get("referenceNumber", None),
            }
