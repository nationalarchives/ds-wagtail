import requests


class KongAPIError(requests.HTTPError):
    """Raised if Kong returns an error instead of results"""


class KongBadRequestError(KongAPIError):
    """Raised if Kong responds with 400"""


class KongInternalServerError(KongAPIError):
    """Raised if Kong responds with 500"""


class KongServiceUnavailableError(KongAPIError):
    """Raised if Kong responds with 503"""


class KongCommunicationError(KongAPIError):
    """Raised if Kong responds with a non-200 status code"""


class SearchManagerException(Exception):
    """Exception to group exceptions raised by SearchManager"""


class InvalidQuery(SearchManagerException):
    """Raised if query to Kong contains no clauses"""


class DoesNotExist(SearchManagerException):
    """Raised if item is requested from Kong but doesn't exist"""


class MultipleObjectsReturned(SearchManagerException):
    """Raised if single item is requested but multiple returned"""


class UnsupportedSlice(ValueError):
    """Raised if unsupported slice is attempted on a SearchManager result set"""
