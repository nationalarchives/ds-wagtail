from typing import Any, Dict

from django.http import HttpRequest


class DataLayerMixin:
    """
    A mixin applied to Page types, Record subclasses,
    or View classes to allow them to customise the Google Analytics
    datalayer.
    """

    def get_gtm_content_group(self) -> str:
        raise NotImplementedError

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Return values that should be included in the Google Analytics datalayer
        when rendering this object for the provided ``request``.

        Override this method on subclasses to add data that is relevant to the
        subclass.
        """

        # Set defaults
        data = {
            "contentGroup1": self.get_gtm_content_group(),
            "customDimension3": "",
            "customDimension4": "",
            "customDimension5": "",
            "customDimension6": "",
            "customDimension7": "",
            "customDimension8": "",
            "customDimension9": "",
            "customDimension10": "",
            "customDimension11": "",
            "customDimension12": "",
            "customDimension13": "",
            "customDimension14": "",
            "customDimension15": "",
            "customDimension16": "",
            "customDimension17": "",
        }

        # Add request-specific data
        # NOTE: Could potentially be added via JS if we want to keep
        # server responses cacheable
        data.update(
            customDimension1="offsite",
            customDimension2=getattr(request.user, "id", ""),
        )
        return data
