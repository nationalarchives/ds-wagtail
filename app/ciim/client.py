import logging

from django.conf import settings
from django.core.cache import cache
from sentry_sdk import capture_message
from tna_utilities.api import SimpleJsonApiClient

logger = logging.getLogger(__name__)

DEFAULT_REFERENCE_NUMBER = "[unknown]"
DEFAULT_SUMMARY_TITLE = "[unknown]"
DEFAULT_IAID = None


class CIIMClient(SimpleJsonApiClient):
    """
    Client for interacting with the CIIM API.
    """

    def __init__(
        self, api_url: str = settings.ROSETTA_API_URL, default_params: dict = None
    ):
        if default_params is None:
            default_params = {}
        super().__init__(api_url, default_params=default_params)
        self.add_default_parameter("filter", "@datatype.base:record")

    def get(self, path: str = "/", default_headers: dict = None) -> dict:
        try:
            return super().get(path=path, default_headers=default_headers)
        except Exception:
            capture_message(
                "CIIMClient.get: Failed to fetch data from CIIM API", level="error"
            )
            return {"data": []}

    def get_record_instance(self) -> dict:
        """
        Get a single record instance from the CIIM API.
        """
        id = self.default_params.get("id")
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

        response = self.get(path="/get", default_headers={})

        if not response or not response.get("data"):
            return {
                "referenceNumber": DEFAULT_REFERENCE_NUMBER,
                "title": DEFAULT_SUMMARY_TITLE,
                "iaid": id,
            }

        try:
            result = response.get("data")[0].get("@template", {}).get("details", {})
        except (IndexError, KeyError):
            result = None
            logger.error(f'Error fetching details in response for IAID "{id}"')

        if result:
            cache.set(
                cache_key,
                result,
                settings.RECORD_DETAILS_CACHE_TIMEOUT,
            )
        else:
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
        id = self.default_params.get("id")

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
