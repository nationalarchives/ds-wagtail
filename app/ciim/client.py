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
        id = self.params.get("id")
        if not id:
            return None

        cache_key = f"record_instance_{id}"
        if cached_record := cache.get(cache_key, None):
            logger.info(
                f'Using cached record for "{id}"',
            )
            return cached_record

        logger.debug(
            f'Getting record instance from CIIM API for ID "{id}"',
        )

        response = self.get(path="/get", headers={})

        if not response or not response.get("data"):
            return {
                "referenceNumber": DEFAULT_REFERENCE_NUMBER,
                "title": DEFAULT_SUMMARY_TITLE,
                "iaid": id,
            }

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
                "iaid": id,
            }
        return result

    def get_serialized_record(self) -> dict:
        """
        Get a standardised serialized record from the CIIM API for the Wagtail API.
        """
        id = self.params.get("id")

        if not id:
            return None

        if instance := self.get_record_instance():
            details = {
                "title": instance.get("summaryTitle")
                or instance.get("title")
                or DEFAULT_SUMMARY_TITLE,
                "iaid": instance.get("iaid", DEFAULT_IAID),
                "reference_number": instance.get(
                    "referenceNumber", DEFAULT_REFERENCE_NUMBER
                ),
            }
            return details
