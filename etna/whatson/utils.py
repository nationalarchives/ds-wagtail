import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import Http404
from requests.exceptions import JSONDecodeError


def eventbrite_api_request_handler(uri, params={}):
    api_url = settings.EVENTBRITE_API_URL
    params["token"] = settings.EVENTBRITE_API_PRIVATE_TOKEN
    url = f"{api_url}/{uri}"
    print(url)
    request = requests.get(url, params=params)
    if request.status_code == 404:
        raise Http404("Resource not found")
    if request.status_code == 400:
        error_detail = None
        try:
            error_detail = request.json().get("error_detail")
        except JSONDecodeError:
            pass
        if error_detail and error_detail.get("ARGUMENTS_ERROR"):
            error_indices = []
            for id in error_detail.get("ARGUMENTS_ERROR"):
                id = id.strip("event_ids.")
                error_indices.append(id)
            return {"error_indices": error_indices}
        raise ValidationError("Bad request")
    if request.status_code == requests.codes.ok:
        try:
            return request.json()
        except JSONDecodeError:
            raise ConnectionError("API provided non-JSON response")
    raise ConnectionError("Request to API failed")


def get_events_listings(page, page_size, params={}):
    uri = "organizations/32190014757/events"
    params.update(
        {
            "page": page,
            "page_size": page_size,
            "order_by": "start_asc",
            "status": "live",
            "expand": "logo,venue,ticket_availability,logo",
        }
    )
    if "start_date.range_start" not in params and "start_date.range_end" not in params:
        params.update(
            {
                "time_filter": "current_future",
            }
        )
    response = eventbrite_api_request_handler(uri, params)
    if "error_indices" in response:
        error_indices = response["error_indices"]
        event_ids_list = params["event_ids"].split(",")
        for index in sorted(error_indices, reverse=True):
            del event_ids_list[int(index)]
        params["event_ids"] = ",".join(event_ids_list)
        return get_events_listings(page, page_size, params)
    return response


def get_event_details(event_id):
    uri = f"events/{event_id}/"
    return eventbrite_api_request_handler(
        uri, params={"expand": "logo,venue,ticket_availability,logo"}
    )
