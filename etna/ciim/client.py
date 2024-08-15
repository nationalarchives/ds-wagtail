import json
import logging

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

from django.utils.functional import cached_property
from django.utils.timezone import get_current_timezone

import requests

from etna.ciim.constants import Aggregation, BucketKeys, VisViews
from etna.records.models import Record

from .exceptions import (
    ClientAPIBadRequestError,
    ClientAPICommunicationError,
    ClientAPIInternalServerError,
    ClientAPIServiceUnavailableError,
    DoesNotExist,
    MultipleObjectsReturned,
)
from .utils import prepare_filter_aggregations, prepare_ohos_params

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


class Sort(StrEnum):
    """Options for sorting /search results by a given field."""

    RELEVANCE = ""
    TITLE_ASC = "title:asc"
    TITLE_DESC = "title:desc"
    DATE_ASC = "date:asc"
    DATE_DESC = "date:desc"


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
                value, supplementary_time or time.min, tzinfo=get_current_timezone()
            )
        return value.isoformat()

    def resultlist_from_response(
        self,
        response_data: Dict[str, Any],
        bucket_counts: List[Dict[str, Union[str, int]]] = None,
        item_type: Type = Record,
    ) -> ResultList:
        try:
            hits = response_data["data"]
            if isinstance(hits, dict):
                hits = [hits]
        except KeyError:
            hits = []
        try:
            total_count = response_data["stats"]["total"]
        except KeyError:
            total_count = len(hits)

        aggregations_data = response_data.get("aggregations", [])
        if bucket_counts is None:
            if not aggregations_data:
                bucket_counts = []
            else:
                pass  # TODO:Rosetta

        return ResultList(
            hits=hits,
            total_count=total_count,
            item_type=item_type,
            aggregations=aggregations_data,
            bucket_counts=bucket_counts,
        )

    def get(
        self,
        *,
        id: Optional[str] = None,
    ) -> Record:
        """Make request and return response for Client API's /get endpoint.
        Used to get a single item by its identifier.
        Keyword arguments:
        id:
            Generic identifier. Matches various id's
            Ex: returns match on Ciim Id, Information Asset Identifier - iaid (or similar primary identifier), creator records faid
        """
        params = {
            "id": id,
        }

        # Get HTTP response from the API
        response = self.make_request(f"{self.base_url}/get", params=params)

        # Convert the HTTP response to a Python dict
        response_data = response.json()

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
        group: Optional[str] = None,
        q: Optional[str] = None,
        # opening_start_date: Optional[Union[date, datetime]] = None,   # TODO: Keep, not in scope for Ohos-Etna at this time
        # opening_end_date: Optional[Union[date, datetime]] = None,   # TODO: Keep, not in scope for Ohos-Etna at this time
        covering_date_from: Optional[Union[date, datetime]] = None,
        covering_date_to: Optional[Union[date, datetime]] = None,
        # stream: Optional[Stream] = None,   # TODO: Keep, not in scope for Ohos-Etna at this time
        aggregations: Optional[List[Aggregation]] = None,
        filter_aggregations: Optional[List[str]] = None,
        # filter_keyword: Optional[str] = None,   # TODO: Keep, not in scope for Ohos-Etna at this time
        sort: Optional[Sort] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
        vis_view: Optional[str] = None,
        long_filter: Optional[bool] = False,
    ) -> ResultList:
        """Make request and return response for Client API's /search endpoint.
        Search all metadata by keyword or web_reference. Results can be
        bucketed, and the search restricted by bucket, reference, topic and
        data stream. If both keyword and web reference are not provided, the
        returned items will be empty.
        Keyword arguments:
        q:
            String to query all indexed fields
        stream:
            Restrict results to given stream
        sort:
            Field to sort results.
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
        vis_view:
            Name of the visualisation view defined for OHOS
        long_filter:
            Handle long filter params for API
        """
        if not aggregations:
            aggregations = []

        if not filter_aggregations:
            filter_aggregations = []

        if group == BucketKeys.COMMUNITY:
            aggregations, filter_aggregations = prepare_ohos_params(
                vis_view, aggregations, filter_aggregations, long_filter
            )

        params = {
            "q": q,
            # "fields": f"stream:{stream}",  # TODO: Keep, not in scope for Ohos-Etna at this time
            "aggs": aggregations,
            "filter": prepare_filter_aggregations(filter_aggregations),
            # "filter": filter_keyword,   # TODO: Keep, not in scope for Ohos-Etna at this time
            "sort": sort,
            "from": offset,
            "size": size,
        }

        # TODO: Keep, not in scope for Ohos-Etna at this time
        #  if opening_start_date:
        #     params["openingStartDate"] = self.format_datetime(
        #         opening_start_date, supplementary_time=time.min
        #     )

        # if opening_end_date:
        #     params["openingEndDate"] = self.format_datetime(
        #         opening_end_date, supplementary_time=time.max
        #     )

        if group == BucketKeys.COMMUNITY:
            if vis_view != VisViews.MAP.value:
                # map view does not have date filters, other visual views have date filters
                # add enrichment date filters with date filter
                if covering_date_from:
                    params["filter"] += [f"fromDate:(>={covering_date_from})"]
                    params["filter"] += [f"enrichmentFrom:(>={covering_date_from})"]

                if covering_date_to:
                    params["filter"] += [f"toDate:(<={covering_date_to})"]
                    params["filter"] += [f"enrichmentTo:(<={covering_date_to})"]
        else:
            if covering_date_from:
                params["filter"] += [f"coveringFromDate:(>={covering_date_from})"]

            if covering_date_to:
                params["filter"] += [f"coveringToDate:(<={covering_date_to})"]

        # Get HTTP response from the API
        response = self.make_request(f"{self.base_url}/search", params=params)

        # Convert the HTTP response to a Python dict
        response_data = response.json()

        bucket_counts_data = []

        # combine enties for all groups across OHOS and TNA
        for bucket in response_data.get("buckets", []):
            if bucket.get("name", "") == "group":
                for entry in bucket.get("entries", []):
                    bucket_counts_data.append(entry)

        # Return a single ResultList, using bucket counts from "buckets",
        # and full hit/aggregation data from "data".
        return self.resultlist_from_response(
            response_data,
            bucket_counts=bucket_counts_data,
        )

    def search_unified(
        self,
        *,
        q: Optional[str] = None,
        web_reference: Optional[str] = None,
        stream: Optional[Stream] = None,
        template: None,  # TODO:Rosetta
        sort_by: Optional[Sort] = None,  # TODO:Rosetta
        sort_order: None,  # TODO:Rosetta
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
        response_data = response.json()

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
        Used to fetch all items by for the given identifier(s).
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
        response_data = response.json()

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
