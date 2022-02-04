from json.decoder import JSONDecodeError


class KongException(Exception):
    """Exception to group exceptions received from Kong client."""


class ConnectionError(KongException):
    """Raised if Kong isn't accessible"""


class KongError(KongException):
    """Raised if Kong returns an error instead of results"""

    def __init__(self, message, response, *args, **kwargs):
        """Attempt to parse out error message from ES."""

        try:
            json = response.json()
        except JSONDecodeError:
            json = {}

        # Parse Elasticsearch error:
        #
        # Expect the following format:
        #
        # "error" : {
        #   "root_cause" : [{
        #     "type" : "illegal_argument_exception",
        #     "reason" : "The bulk request must be terminated by a newline [\n]"
        #   }],
        #   "type" : "illegal_argument_exception",
        #   "reason" : "The bulk request must be terminated by a newline [\n]"
        # },
        # "status" : 400
        try:
            message = f'{message} {json["error"]["reason"]}'
        except (KeyError, TypeError):
            # Failed to find error message, in Elasticseach error
            pass

        # Parse Kubernetes or Kong error response:
        #
        # Expect the following format:
        #
        # {
        #   "timestamp": "2022-02-04T13:46:22.445",
        #   "status": "Bad Request",
        #   "statusCode": 400,
        #   "message": "Failed to convert value of type 'java.lang.String' to required type 'java.lang.Boolean';",
        #   "path": "/api/v1/data/fetch"
        # }
        try:
            message = f'{message} {json["message"]}'
        except KeyError:
            # Failed to find error message, in Elasticseach error
            pass

        super().__init__(message, *args, **kwargs)


class SearchManagerException(KongException):
    """Exception to group exceptions raised by SearchManager"""


class InvalidQuery(SearchManagerException):
    """Raised if query to Kong contains no clauses"""


class DoesNotExist(SearchManagerException):
    """Raised if item is requested from Kong but doesn't exist"""


class MultipleObjectsReturned(SearchManagerException):
    """Raised if single item is requested but multiple returned"""


class UnsupportedSlice(ValueError):
    """Raised if unsupported slice is attempted on a SearchManager result set"""
