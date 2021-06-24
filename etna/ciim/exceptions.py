class KongException(Exception):
    """Exception to group exceptions received from Kong client."""

class ConnectionError(KongException):
    """Raised if Kong isn't accessible"""

class InvalidResponse(KongException):
    """Raised if Kong returns non-200 reponse"""


class KubernetesError(KongException):
    """Raised if kubernetes returns an error instead of results"""


class KongError(KongException):
    """Raised if Kong returns an error instead of results"""


class SearchManagerException(Exception):
    """Exception to group exceptions raised by SearchManager"""


class DoesNotExist(SearchManagerException):
    """Raised if item is requested from Kong but doesn't exist"""


class MultipleObjectsReturned(SearchManagerException):
    """Raised if single item is requested but multiple returned"""
