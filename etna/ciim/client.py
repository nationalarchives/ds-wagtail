import enum
import json
import logging
import re

from datetime import datetime
from typing import Any, Optional

import requests

from .exceptions import (
    KongBadRequestError,
    KongCommunicationError,
    KongInternalServerError,
    KongServiceUnavailableError,
)

logger = logging.getLogger(__name__)


class Stream(str, enum.Enum):
    """Options for restricting /search results to a given stream.

    Evidential:
        Catalogue data i.e: Records

    interpretive:
        Any content written _about_ evidential i.e: Research Guides, Blog posts
    """

    EVIDENTIAL = "evidential"
    INTERPRETIVE = "interpretive"


class SortBy(str, enum.Enum):
    """Options for sorting /search results by a given field."""

    RELEVANCE = ""
    TITLE = "title"
    DATE_CREATED = "dateCreated"
    DATE_OPENING = "dateOpening"


class SortOrder(str, enum.Enum):
    """Options for sort order for /search results."""

    ASC = "asc"
    DESC = "desc"


class Template(str, enum.Enum):
    """@template block to include with response.

    Supported by all endpoints.
    """

    DETAILS = "details"
    RESULTS = "results"


class Aggregation(str, enum.Enum):
    """Aggregated counts to include with response.

    Supported by /search and /searchAll endpoints.
    """

    TOPIC = "topic"
    COLLECTION = "collection"
    GROUP = "group"
    LEVEL = "level"
    CLOSURE = "closure"
    CATALOGUE_SOURCE = "catalogueSource"
    HELD_BY = "heldBy"


def prepare_filter_aggregations(items: Optional[list]) -> Optional[str]:
    """
    Filter format in items: 'field:value', 'field:value:or'
    Prepares i.e. removes/replaces special chars from a filter fields' value to be passed to the api
    When using filter with multiple values, specific fields require OR operator to be specified,
    otherwise AND is used by default.

    Example:
    before-prepare: "heldBy:Birmingham: Archives, Heritage and Photography Service"
    after-prepare:  "heldBy:Birmingham Archives Heritage and Photography Service"
    before-prepare: "heldBy:Staffordshire and Stoke-on-Trent Archive Service: Staffordshire County Record Office"
    after-prepare:  "heldBy:Staffordshire and Stoke on Trent Archive Service Staffordshire County Record Office"
    Special char single quote i.e. ' is not prepared
    before-prepare: "heldBy:Labour History Archive and Study Centre (People's History Museum/University of Central Lancashire)"
    after-prepare:  "heldBy:Labour History Archive and Study Centre People's History Museum University of Central Lancashire "
    """
    if not items:
        return None

    regex = r"([/():,\&\-\|+@!.])"
    subst = " "
    field_list_to_prepare = ["heldBy"]
    filter_prepared_list = []
    fields_using_or_operator = ["heldBy", "collection"]

    for item in items:
        field, value = item.split(":", 1)
        if field in field_list_to_prepare:
            # replace special chars
            prepared_value = re.sub(regex, subst, value, 0, re.MULTILINE)
            # replace multiple space
            prepared_value = re.sub(" +", subst, prepared_value, 0, re.MULTILINE)
            filter_prepared = (
                field + ":" + re.sub(regex, subst, prepared_value, 0, re.MULTILINE)
            )
        else:
            filter_prepared = field + ":" + value

        filter_prepared_list.append(filter_prepared)

    # if number of occurrences of field_for_or is more than 1, update add or to those values
    # ["collection:<value1>:or", "collection:<value2>:or", "group:<value3>"]
    for field in fields_using_or_operator:
        # more than 1 value for the field
        if sum((item.split(":", 1)[0].count(field) for item in items)) > 1:
            # append or to the value for each field
            updated_list_for_or_operator = []
            for item in filter_prepared_list:
                if item.split(":", 1)[0] == field:
                    updated_list_for_or_operator.append(item + ":or")
                else:
                    updated_list_for_or_operator.append(item)

            filter_prepared_list = updated_list_for_or_operator

    return filter_prepared_list


class KongClient:
    """Client used to Fetch and validate data from Kong."""

    http_error_classes = {
        400: KongBadRequestError,
        500: KongInternalServerError,
        503: KongServiceUnavailableError,
    }
    default_http_error_class = KongCommunicationError

    def __init__(
        self,
        base_url: str,
        api_key: str,
        verify_certificates: bool = True,
        timeout: int = 5,
    ):
        self.base_url: str = base_url
        self.session = requests.Session()
        self.session.headers.update({"apikey": api_key})
        self.session.verify = verify_certificates
        self.timeout = timeout

    def fetch(
        self,
        *,
        iaid: Optional[str] = None,
        id: Optional[str] = None,
        template: Optional[Template] = None,
        expand: Optional[bool] = None,
    ) -> dict:
        """Make request and return response for Kong's /fetch endpoint.

        Used to fetch a single item by its identifier.

        Keyword arguments:

        iaid:
            Return match on Information Asset Identifier
        id:
            Generic identifier. Matches on references_number or iaid
        template:
            @template data to include with response
        expand:
            include @next and @previous record with response. Kong defaults to false
        """
        params = {
            "iaid": iaid,
            "id": id,
            "template": template,
            "expand": expand,
        }

        return self.make_request(f"{self.base_url}/data/fetch", params=params).json()

    def search(
        self,
        *,
        q: Optional[str] = None,
        web_reference: Optional[str] = None,
        opening_start_date: Optional[datetime] = None,
        opening_end_date: Optional[datetime] = None,
        created_start_date: Optional[datetime] = None,
        created_end_date: Optional[datetime] = None,
        stream: Optional[Stream] = None,
        sort_by: Optional[SortBy] = None,
        sort_order: Optional[SortOrder] = None,
        template: Optional[Template] = None,
        aggregations: Optional[list[Aggregation]] = None,
        filter_aggregations: Optional[list[str]] = None,
        filter_keyword: Optional[str] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
    ) -> dict:
        """Make request and return response for Kong's /fetch endpoint.

        Search all metadata by keyword or web_reference. Results can be
        bucketed, and the search restricted by bucket, reference, topic and
        data stream. If both keyword and web reference are not provided, the
        returned items will be empty.

        Keyword arguments:

        q:
            String to query all indexed fields
        web_reference:
            Return matches on references_number
        stream:
            Restrict results to given stream
        sort_by:
            Field to sort results.
        sortOrder:
            Order of sorted results
        template:
            @template data to include with response
        aggregations:
            aggregations to include with response. Number returned can be set
            by optional count suffix: <aggregation>:<number-to-return>
        filter_aggregations:
            filter results set by aggregation
        filter_keyword:
            filter results by keyword
        offset:
            Offset for results. Mapped to 'from' before making request
        size:
            Number of results to return
        """
        params = {
            "q": q,
            "webReference": web_reference,
            "stream": stream,
            "sort": sort_by,
            "sortOrder": sort_order,
            "template": template,
            "aggregations": aggregations,
            "filterAggregations": prepare_filter_aggregations(filter_aggregations),
            "filter": filter_keyword,
            "from": offset,
            "size": size,
        }

        if opening_start_date:
            params["openingStartDate"] = opening_start_date.isoformat()

        if opening_end_date:
            params["openingEndDate"] = opening_end_date.isoformat()

        if created_start_date:
            params["createdStartDate"] = created_start_date.isoformat()

        if created_end_date:
            params["createdEndDate"] = created_end_date.isoformat()

        return self.make_request(f"{self.base_url}/data/search", params=params).json()

    def search_all(
        self,
        *,
        q: Optional[str] = None,
        aggregations: Optional[list[Aggregation]] = None,
        filter_aggregations: Optional[list[str]] = None,
        template: Optional[Template] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
    ) -> dict:
        """Make request and return response for Kong's /fetch endpoint.

        Search metadata across multiple buckets in parallel. Returns results
        and an aggregation for each provided bucket

        Keyword arguments:

        q:
            String to query all indexed fields
        aggregations:
            aggregations to include with response. Number returned can be set
            by optional count suffix: <aggregation>:<number-to-return>
        filter_aggregations:
            filter results set by aggregation
        template:
            @template data to include with response
        offset:
            Offset for results. Mapped to 'from' before making request
        size:
            Number of results to return
        """
        params = {
            "q": q,
            "aggregations": aggregations,
            "filterAggregations": prepare_filter_aggregations(filter_aggregations),
            "template": template,
            "from": offset,
            "size": size,
        }

        return self.make_request(
            f"{self.base_url}/data/searchAll", params=params
        ).json()

    def search_unified(
        self,
        *,
        q: Optional[str] = None,
        web_reference: Optional[str] = None,
        stream: Optional[Stream] = None,
        template: Optional[Template] = None,
        sort_by: Optional[SortBy] = None,
        sort_order: Optional[SortOrder] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
    ) -> dict:
        """Make request and return response for Kong's /searchUnified endpoint.

        /searchUnified reproduces the private beta???s /search endpoint, turning
        a single response for a q, webReference-based query.

        Search all metadata by title, identifier or web reference. Unlike the
        main search endpoint, boolean operators, aggregations and filtering are
        NOT supported.

        Keyword arguments:

        q:
            String to query all indexed fields
        web_reference:
            Return matches on references_number
        stream:
            Restrict results to given stream
        template:
            @template data to include with response
        sort_by:
            Field to sort results.
        sort_order:
            Order of sorted results
        offset:
            Offset for results. Mapped to 'from' before making request
        size:
            Number of results to return
        """
        params = {
            "q": q,
            "webReference": web_reference,
            "stream": stream,
            "template": template,
            "sort": sort_by,
            "sortOrder": sort_order,
            "from": offset,
            "size": size,
        }

        return self.make_request(
            f"{self.base_url}/data/searchUnified", params=params
        ).json()

    def fetch_all(
        self,
        *,
        ids: Optional[list[str]] = None,
        iaids: Optional[list[str]] = None,
        rid: Optional[str] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
    ) -> dict:
        """Make request and return response for Kong's /fetchAll endpoint.

        Used to fetch a all items by for the given identifier(s).

        Fetch all metadata with a generic identifier, iaid or replicaId (rid).

        Keyword arguments:

        ids:
            Generic identifiers. Matches on references_number or iaid
        iaids:
            Return matches on Information Asset Identifier
        rid:
            Return matches on replic ID
        offset:
            Offset for results. Mapped to 'from' before making request
        size:
            Number of results to return
        """
        params = {
            "ids": ids,
            "iaids": iaids,
            "rid": rid,
            "from": offset,
            "size": size,
        }

        return self.make_request(f"{self.base_url}/data/fetchAll", params=params).json()

    def prepare_request_params(
        self, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Process parameters before passing to Kong.

        Remove empty values to make logged requests cleaner.
        """
        if not data:
            return {}

        return {k: v for k, v in data.items() if v is not None}

    def make_request(
        self, url: str, params: Optional[dict[str, Any]] = None
    ) -> requests.Response:
        """Make request to Kong API."""
        params = self.prepare_request_params(params)
        response = self.session.get(url, params=params, timeout=self.timeout)
        self._raise_for_status(response)
        return response

    def _raise_for_status(self, response: requests.Response) -> None:
        """Raise custom error for any requests.HTTPError raised for a request.

        KongAPIErrors include response body in message to aide debugging.
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
