import json
import logging
import re
from collections.abc import Sequence
from datetime import date, datetime, time
from enum import StrEnum
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

import requests
from django.utils.functional import cached_property
from django.utils.timezone import get_current_timezone
from sentry_sdk import capture_message

from etna.ciim.constants import Aggregation
from etna.records.models import Record

from .exceptions import (
    ClientAPIBadRequestError,
    ClientAPICommunicationError,
    ClientAPIInternalServerError,
    ClientAPIServiceUnavailableError,
    DoesNotExist,
    MultipleObjectsReturned,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from etna.ciim.models import APIModel


class Stream(StrEnum):
    """Options for restricting /search results to a given stream.

    Evidential:
        Catalogue data i.e: Records

    interpretive:
        Any content written _about_ evidential i.e: Research Guides, Blog posts
    """

    EVIDENTIAL = "evidential"
    INTERPRETIVE = "interpretive"


class SortBy(StrEnum):
    """Options for sorting /search results by a given field."""

    RELEVANCE = ""
    TITLE = "title"
    DATE_CREATED = "dateCreated"
    DATE_OPENING = "dateOpening"


class SortOrder(StrEnum):
    """Options for sort order for /search results."""

    ASC = "asc"
    DESC = "desc"


class Template(StrEnum):
    """@template block to include with response.

    Supported by all endpoints.
    """

    DETAILS = "details"
    RESULTS = "results"


def prepare_filter_aggregations(
    items: Sequence[str] | None,
) -> list[str] | None:
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
    fields_using_or_operator = ["heldBy", "collection", "level"]

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


class ResultList:
    """
    A convenience class that lazily converts a raw list of "hits" (from various
    API endpoints) into instances of `item_type` when iterated, as well
    providing the following developer-friendly helper attributes:

    `total_count`:
        The total number of results available

    `aggregations`:
        A dict of "aggregation" values from the results themselves

    `bucket_counts`:
        A list of count values for each 'bucket'
    """

    def __init__(
        self,
        hits: Sequence[Dict[str, Any]],
        total_count: int,
        item_type: Type,
        aggregations: Dict[str, Any],
        bucket_counts: List[Dict[str, Union[str, int]]],
    ):
        self._hits = hits or []
        self.total_count = total_count
        self.item_type = item_type
        self.aggregations = aggregations
        self.bucket_counts = bucket_counts

    @cached_property
    def hits(self) -> Tuple["APIModel"]:
        """
        Return a tuple of APIModel instances representative of the raw `_hits`
        data. The return value is cached to support reuse without any
        transformation overhead.
        """
        return tuple(
            self.item_type.from_api_response(h) if isinstance(h, dict) else h
            for h in self._hits
        )

    def __iter__(self) -> Iterable["APIModel"]:
        yield from self.hits

    def __len__(self) -> int:
        return len(self._hits)

    def __bool__(self) -> bool:
        return bool(self._hits)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name} {self.hits}>"


class ClientAPI:
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
        api_key: str,
        verify_certificates: bool = True,
        timeout: int = 5,
    ):
        self.base_url: str = base_url
        self.session = requests.Session()
        self.session.headers.update({"apikey": api_key})
        self.session.verify = verify_certificates
        self.timeout = timeout

    @staticmethod
    def format_datetime(
        value: Union[date, datetime], supplementary_time: Optional[time] = None
    ) -> datetime:
        """
        Converts a `date` or `datetime` value to an isoformat string that the API
        will understand. If value is `date`, it will be converted into a `datetime`,
        using `supplementary_time` for the time information (defaulting to 00:00:00
        if not provided).
        """
        if not isinstance(value, datetime):
            value = datetime.combine(
                value,
                supplementary_time or time.min,
                tzinfo=get_current_timezone(),
            )
        return value.isoformat()

    def resultlist_from_response(
        self,
        response_data: Dict[str, Any],
        bucket_counts: List[Dict[str, Union[str, int]]] = None,
        item_type: Type = Record,
    ) -> ResultList:
        try:
            hits = response_data["hits"]["hits"]
        except KeyError:
            hits = []
        try:
            total_count = response_data["hits"]["total"]["value"]
        except KeyError:
            total_count = len(hits)

        aggregations_data = response_data.get("aggregations", {})
        if bucket_counts is None:
            bucket_counts = aggregations_data.get("group", {}).get("buckets", [])

        return ResultList(
            hits=hits,
            total_count=total_count,
            item_type=item_type,
            aggregations=aggregations_data,
            bucket_counts=bucket_counts,
        )

    def fetch(
        self,
        *,
        iaid: Optional[str] = None,
        id: Optional[str] = None,
        template: Optional[Template] = None,
        expand: Optional[bool] = None,
    ) -> Record:
        """Make request and return response for Client API's /fetch endpoint.

        Used to fetch a single item by its identifier.

        Keyword arguments:

        iaid:
            Return match on Information Asset Identifier - iaid (or similar primary identifier)
        id:
            Generic identifier. Matches on references_number or iaid
        template:
            @template data to include with response
        expand:
            include @next and @previous record with response. Client API defaults to false
        """
        params = {
            # Yes 'metadata_id' is inconsistent with the 'iaid' argument name, but this
            # API argument name is temporary, and 'iaid' will be replaced more broadly with
            # something more generic soon
            "metadataId": iaid,
            "id": id,
            "template": template,
            "expand": expand,
        }

        # Get HTTP response from the API
        response = self.make_request(f"{self.base_url}/fetch", params=params)

        # Convert the HTTP response to a Python dict
        response_data = self.decode_json_response(response)

        # Convert the Python dict to a ResultList
        result_list = self.resultlist_from_response(response_data)

        if not result_list:
            raise DoesNotExist
        if len(result_list) > 1:
            raise MultipleObjectsReturned
        return result_list.hits[0]

    def search(
        self,
        *,
        q: Optional[str] = None,
        web_reference: Optional[str] = None,
        opening_start_date: Optional[Union[date, datetime]] = None,
        opening_end_date: Optional[Union[date, datetime]] = None,
        created_start_date: Optional[Union[date, datetime]] = None,
        created_end_date: Optional[Union[date, datetime]] = None,
        stream: Optional[Stream] = None,
        sort_by: Optional[SortBy] = None,
        sort_order: Optional[SortOrder] = None,
        template: Optional[Template] = None,
        aggregations: Optional[list[Aggregation]] = None,
        filter_aggregations: Optional[list[str]] = None,
        filter_keyword: Optional[str] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
    ) -> ResultList:
        """Make request and return response for Client API's /search endpoint.

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
            params["openingStartDate"] = self.format_datetime(
                opening_start_date, supplementary_time=time.min
            )

        if opening_end_date:
            params["openingEndDate"] = self.format_datetime(
                opening_end_date, supplementary_time=time.max
            )

        if created_start_date:
            params["createdStartDate"] = self.format_datetime(
                created_start_date, supplementary_time=time.min
            )

        if created_end_date:
            params["createdEndDate"] = self.format_datetime(
                created_end_date, supplementary_time=time.max
            )

        # Get HTTP response from the API
        response = self.make_request(f"{self.base_url}/search", params=params)

        # Convert the HTTP response to a Python dict
        response_data = self.decode_json_response(response)

        # Pull out the separate ES responses
        bucket_counts_data, results_data = response_data["responses"]

        # Return a single ResultList, using bucket counts from the first ES response,
        # and full hit/aggregation data from the second.
        return self.resultlist_from_response(
            results_data,
            bucket_counts=bucket_counts_data["aggregations"]
            .get("group", {})
            .get("buckets", ()),
        )

    def search_all(
        self,
        *,
        q: Optional[str] = None,
        aggregations: Optional[list[Aggregation]] = None,
        filter_aggregations: Optional[list[str]] = None,
        template: Optional[Template] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
    ) -> Tuple[ResultList]:
        """Make request and return response for Client API's /searchAll endpoint.

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

        # Get HTTP response from the API
        response = self.make_request(f"{self.base_url}/searchAll", params=params)

        # Convert the HTTP response to a Python dict
        response_data = self.decode_json_response(response)

        # The API returns a series of ES 'responses', with results for each 'bucket'.
        # Each of these responses is converted to it's own `ResultList`, and the collective
        # `ResultList` objects returned as tuple.
        return tuple(
            self.resultlist_from_response(r) for r in response_data.get("responses", ())
        )

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
    ) -> ResultList:
        """Make request and return response for Client API's /searchUnified endpoint.

        /searchUnified reproduces the private beta’s /search endpoint, turning
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

        # Get HTTP response from the API
        response = self.make_request(f"{self.base_url}/searchUnified", params=params)

        # Convert the HTTP response to a Python dict
        response_data = self.decode_json_response(response)

        # The API returns a single ES response for this endpoint, which can be directly converted
        # to a ResultList.
        return self.resultlist_from_response(response_data)

    def fetch_all(
        self,
        *,
        ids: Optional[list[str]] = None,
        iaids: Optional[list[str]] = None,
        rid: Optional[str] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
    ) -> ResultList:
        """Make request and return response for Client API's /fetchAll endpoint.

        Used to fetch a all items by for the given identifier(s).

        Fetch all metadata with a generic identifier, iaid or replicaId (rid).

        Keyword arguments:

        ids:
            Generic identifiers. Matches on references_number or iaid
        iaids:
            Return matches on Information Asset Identifier - iaid (or similar primary identifier)
        rid:
            Return matches on replic ID
        offset:
            Offset for results. Mapped to 'from' before making request
        size:
            Number of results to return
        """
        params = {
            # Yes 'metadata_id' is inconsistent with the 'iaid' argument name, but this
            # API argument name is temporary, and 'iaid' will be replaced more broadly with
            # something more generic soon
            "metadataIds": iaids,
            "ids": ids,
            "rid": rid,
            "from": offset,
            "size": size,
        }

        # Get HTTP response from the API
        response = self.make_request(f"{self.base_url}/fetchAll", params=params)

        # Convert the HTTP response to a Python dict
        response_data = self.decode_json_response(response)

        # The API returns a single ES response for this endpoint, which can be directly converted
        # to a ResultList.
        return self.resultlist_from_response(response_data)

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
        try:  # TODO: This is a hack to prevent CIIM failures from being raised as exceptions that break the site, make this better
            self._raise_for_status(response)
        except Exception:
            capture_message(
                f"Client API request failed with status code {response.status_code}",
                level="error",
            )
        return response

    def decode_json_response(self, response):
        """Returns decoded JSON data using the built-in json decoder"""
        try:
            return response.json()
        except ValueError as e:
            # log exception value with response body
            logger.error(f"{str(e)}:Response body:{response.text}")
            # suppress double exception raising, keeping original exception available
            raise Exception(e) from None

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
