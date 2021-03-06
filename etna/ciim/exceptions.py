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


class APIManagerException(Exception):
    """Exception to group exceptions raised by APIManager"""


class DoesNotExist(APIManagerException):
    """Raised if item is requested from Kong but doesn't exist"""


class MultipleObjectsReturned(APIManagerException):
    """Raised if single item is requested but multiple returned"""
