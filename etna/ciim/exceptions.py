import requests


class ClientAPIError(requests.HTTPError):
    """Raised if Client API returns an error instead of results"""


class ClientAPIBadRequestError(ClientAPIError):
    """Raised if Client API responds with 400"""


class ClientAPIInternalServerError(ClientAPIError):
    """Raised if Client API responds with 500"""


class ClientAPIServiceUnavailableError(ClientAPIError):
    """Raised if Client API responds with 503"""


class ClientAPICommunicationError(ClientAPIError):
    """Raised if Client API responds with a non-200 status code"""


class DoesNotExist(ClientAPIError):
    """Raised if item is requested from Client API but doesn't exist"""


class MultipleObjectsReturned(ClientAPIError):
    """Raised if single item is requested but multiple returned"""
