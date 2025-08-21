import logging

from django.conf import settings
from django.core.cache import cache
from sentry_sdk import capture_message

from app.core.json_api_client import JSONAPIClient

logger = logging.getLogger(__name__)

DEFAULT_REFERENCE_NUMBER = "[unknown]"
DEFAULT_SUMMARY_TITLE = "[unknown]"
DEFAULT_IAID = None


class CIIMClient(JSONAPIClient):
    """
    Client for interacting with the CIIM API.
    """

    def __init__(self, api_url: str = settings.ROSETTA_API_URL, params: dict = {}):
        super().__init__(api_url, params=params)
        self.add_parameter("filter", "@datatype.base:record")

    def get(self, path: str = "/", headers: dict = None) -> dict:
        try:
            return super().get(path=path, headers=headers)
        except Exception:
            capture_message(
                "CIIMClient.get: Failed to fetch data from CIIM API", level="error"
            )
            return {"data": []}

    def get_record_instance(self) -> dict:
        """
        Get a single record instance from the CIIM API.
        """

        if not self.params.get("id"):
            return None

        cache_key = f"record_instance_{self.params.get('id')}"
        if cached_record := cache.get(cache_key, None):
            logger.info(
                f"Using cached record for \"{self.params.get('id')}\"",
            )
            return cached_record

        logger.debug(
            f"Getting record instance from CIIM API for ID \"{self.params.get('id')}\"",
        )

        response = self.get(path="/get", headers={})

        if not response or not response.get("data"):
            return None

        try:
            result = response.get("data")[0].get("@template", {}).get("details", {})
            cache.set(
                cache_key,
                result,
                settings.RECORD_DETAILS_CACHE_TIMEOUT,
            )
        except IndexError:
            result = {
                "referenceNumber": DEFAULT_REFERENCE_NUMBER,
                "title": DEFAULT_SUMMARY_TITLE,
                "iaid": self.params.get("id", DEFAULT_IAID),
            }
        return result

    def get_serialized_record(self) -> dict:
        """
        Get a standardised serialized record from the CIIM API for the Wagtail API.
        """

        if not self.params.get("id") or self.params.get("id") is None:
            return None

        if instance := self.get_record_instance():
            details = {
                "title": instance.get("title", DEFAULT_SUMMARY_TITLE)
                or instance.get("summaryTitle", DEFAULT_SUMMARY_TITLE),
                "iaid": instance.get("iaid", DEFAULT_IAID),
                "reference_number": instance.get(
                    "referenceNumber", DEFAULT_REFERENCE_NUMBER
                ),
            }
            return details
