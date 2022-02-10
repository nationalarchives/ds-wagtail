import enum
import json
import logging

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

    TITLE = "title"
    DATE_CREATED = "date_created"


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


def format_list_param(items: Optional[list]) -> Optional[str]:
    """Convenience function to transform list to comma-separated string.

    When parsing a request's parameters `requests` uses `urllib.parse.urlencode`
    with the deseq flag set to true, transforming a list's values into multiple
    parameters:

    >>> urllib.parse.urlencode({'param': ['item-1', 'item-2']}, doseq=True)
    'param=item-1&param=item-2'

    https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode

    Kong expects multiple values to be a in a comma-separated string:

    'param=item-1,+item-2'

    This function, when given a list, will return a comma-separated string.
    """
    if not items:
        return None
    return ", ".join(items)


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

        # remove empty values to make logged requests cleaner.
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = self.session.get(
                f"{self.base_url}/data/fetch", params=params, timeout=self.timeout
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e

        return self.validate_and_parse_response(response)

    def search(
        self,
        *,
        keyword: Optional[str] = None,
        web_reference: Optional[str] = None,
        stream: Optional[Stream] = None,
        sort_by: Optional[SortBy] = None,
        sort_order: Optional[SortOrder] = None,
        template: Optional[Template] = None,
        show_buckets: Optional[bool] = None,
        buckets: Optional[list[str]] = None,
        topics: Optional[list[str]] = None,
        references: Optional[list[str]] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
    ) -> dict:
        """Make request and return response for Kong's /fetch endpoint.

        Search all metadata by keyword or web_reference. Results can be
        bucketed, and the search restricted by bucket, reference, topic and
        data stream. If both keyword and web reference are not provided, the
        returned items will be empty.

        Keyword arguments:

        keyword:
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
        show_buckets:
            Include Etna search buckets with response
        buckets:
            Restrict results to given bucket(s)
        topics:
            Restrict results to given topic(s)
        references:
            Restrict results to given reference(s)
        offset:
            Offset for results. Mapped to 'from' before making request
        size:
            Number of results to return
        """
        params = {
            "keyword": keyword,
            "webReference": web_reference,
            "stream": stream,
            "sort": sort_by,
            "sortOrder": sort_order,
            "template": template,
            "showBuckets": show_buckets,
            "buckets": format_list_param(buckets),
            "topics": format_list_param(topics),
            "references": format_list_param(references),
            "from": offset,
            "size": size,
        }

        # remove empty values to make logged requests cleaner.
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = self.session.get(
                f"{self.base_url}/data/search", params=params, timeout=self.timeout
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e

        return self.validate_and_parse_response(response)

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
            "ids": format_list_param(ids),
            "iaids": format_list_param(iaids),
            "rid": rid,
            "from": offset,
            "size": size,
        }

        # remove empty values to make logged requests cleaner.
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = self.session.get(
                f"{self.base_url}/data/fetchAll", params=params, timeout=self.timeout
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError from e

        return self.validate_and_parse_response(response)

    def validate_and_parse_response(self, response: requests.Response) -> dict:
        """Validates response pre-JSON decode."""
        if not response.ok:
            raise KongError("Invalid response.", response=response)

        json = response.json()

        logger.debug(f"Response from Kong: {json}")

        return json
