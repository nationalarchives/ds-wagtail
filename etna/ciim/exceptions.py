import requests


class KongAPIError(requests.HTTPError):
    """Raised if Kong returns an error instead of results"""


class KongBadRequestError(KongAPIError):
    """Raised if Kong responds with 400"""


class KongInternalServerError(KongAPIError):
    """Raised if Kong responds with 500"""


class KongServiceUnavailableError(KongAPIError):
    """Raised if Kong responds with 503"""


class KongRecordNotFound(KongAPIError):
    """Raised if Kong responds with a 404, or if an endpoint
    that is supposed to return a single record returns an empty list"""


class KongCommunicationError(KongAPIError):
    """Raised if Kong responds with a non-200 status code"""


class KongAmbiguousRecordIdentifier(KongAPIError):
    """Raised if Kong returns multiple records for an endpoint that
    is supposed to return a single record"""


class APIManagerException(Exception):
    """Exception to group exceptions raised by APIManager"""
