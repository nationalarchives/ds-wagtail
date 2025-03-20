from django.conf import settings
from requests.exceptions import JSONDecodeError

from etna.core.api import APIClientError, JSONAPIClient


class EventbriteAPIClient(JSONAPIClient):
    """
    A client for interacting with the Eventbrite API.
    """

    EVENTBRITE_API_URL = settings.EVENTBRITE_API_URL
    EVENTBRITE_API_PRIVATE_TOKEN = settings.EVENTBRITE_API_PRIVATE_TOKEN
    ORGANIZATION_ID = "32190014757"

    def __init__(self):
        super().__init__(
            api_url=self.EVENTBRITE_API_URL,
            params={"token": self.EVENTBRITE_API_PRIVATE_TOKEN},
        )

    def get(self, path: str = "/", headers: dict = None) -> dict:
        """
        Extends the get method to handle specific error responses from the Eventbrite API.
        """
        try:
            response = super().get(path, headers)
        except APIClientError as e:
            return self._handle_eventbrite_apiclienterror(e)
        return response

    def _handle_api_client_error(self, error: APIClientError) -> dict:
        """
        Handle specific error responses from the Eventbrite API.
        """
        error_detail = None
        try:
            error_detail = error.response.json().get("error_detail")
        except JSONDecodeError:
            pass
        if error_detail and error_detail.get("ARGUMENTS_ERROR"):
            error_indices = []
            for id in error_detail.get("ARGUMENTS_ERROR"):
                id = id.strip("event_ids.")
                error_indices.append(id)
            return {"error_indices": error_indices}
        raise error

    def get_event_details(self, event_id: str) -> dict:
        """
        Get the details of a specific event by its ID.
        """
        self.add_parameters({"expand": "logo,venue,ticket_availability,logo"})
        return self.get(path=f"events/{event_id}/")

    def get_event_listings(self, page: int, page_size: int, params: dict = {}) -> dict:
        """
        Give a list of our published event IDs, return a list of valid events from the Eventbrite API.
        Includes logic to remove any invalid event IDs from the list if a 400 error is raised.
        """
        self.add_parameters(
            {
                "page": page,
                "page_size": page_size,
                "order_by": "start_asc",
                "status": "live",
                "expand": "logo,venue,ticket_availability,logo",
                **params,
            }
        )

        if (
            "start_date.range_start" not in params
            and "start_date.range_end" not in params
        ):
            self.add_parameters({"time_filter": "current_future"})

        response = self.get(path=f"organizations/{self.ORGANIZATION_ID}/events")

        if error_indices := response.get("error_indices", []):
            event_ids_list = params.get("event_ids", "").split(",")
            for index in sorted(error_indices, reverse=True):
                del event_ids_list[int(index)]
            params["event_ids"] = ",".join(event_ids_list)
            return self.get_event_listings(page, page_size, params)

        return response
