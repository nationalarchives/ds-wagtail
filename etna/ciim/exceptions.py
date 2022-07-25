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


class DoesNotExist(KongAPIError):
    """Raised if item is requested from Kong but doesn't exist"""


class MultipleObjectsReturned(KongAPIError):
    """Raised if single item is requested but multiple returned"""
