class KongException(Exception):
    """Exception to group exceptions received from Kong client."""


class ConnectionError(KongException):
    """Raised if Kong isn't accessible"""


class InvalidResponse(KongException):
    """Raised if Kong returns non-200 reponse"""

    def __init__(self, message, *args, **kwargs):
        """Attempt to parse out error message from ES."""

        self.json = kwargs.pop("json", {})

        try:
            reason = self.json["error"]["root_cause"][0]["reason"]
            message = f"{message} Reason: {reason}"
        except (IndexError, KeyError, TypeError):
            """Failed to find error message, raise without message"""

        super().__init__(message, *args, **kwargs)


class KubernetesError(KongException):
    """Raised if kubernetes returns an error instead of results"""


class KongError(KongException):
    """Raised if Kong returns an error instead of results"""


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
