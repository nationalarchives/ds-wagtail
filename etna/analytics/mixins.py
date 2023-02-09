from typing import Any, Dict

from django.http import HttpRequest


class DataLayerMixin:
    """
    A mixin applied to Page types, Record subclasses,
    or View classes to allow them to customise the Google Analytics
    datalayer.
    """

    gtm_content_group: str = None

    def get_gtm_content_group(self) -> str:
        """
        Return a string to use as the 'contentGroup1' value in DataLayer
        for this object.

        For most cases, setting `gtm_content_group` on the class should be
        sufficient, but this method can be overridden to support cases where
        different per-instance values are required.
        """
        if self.get_gtm_content_group is None:
            raise NotImplementedError(
                f"You must set the 'gtm_content_group' attribute on {self.__class__} to a string. Alternatively, you can override the 'get_gtm_content_group()' method to return a different value(s)."
            )
        return self.gtm_content_group

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Return values that should be included in the Google Analytics datalayer
        when rendering this object for the provided ``request``.

        Override this method on subclasses to add data that is relevant to the
        subclass.
        """

        # Set defaults
        data = {
            "contentGroup1": self.get_gtm_content_group(),  # The name of the content group - [Always has a value]
            "customDimension1": "",  # The reader type (options are "offsite",
            # "onsite_public", "onsite_staff", "subscription")
            "customDimension2": "",  # The user type and is private beta specific
            # - the user ID for participants."customDimension3": ""
            "customDimension3": "",  # The page type - [Always has a value]
            "customDimension4": "",  # Taxonomy topics for the page, delineated by semi-colons. Empty string if no value.
            "customDimension5": "",  # This is the taxonomy sub topic where applicable. Empty string if not applicable.
            "customDimension6": "",  # This is the taxonomy term where applicable. Empty string if not applicable.
            "customDimension7": "",  # This is the time period where applicable. Empty string if not applicable.
            "customDimension8": "",  # This is the sub time period where applicable. Empty string if not applicable.
            "customDimension9": "",  # This is the entity type where applicable. Empty string if not applicable.
            "customDimension10": "",  # This is the entity label where applicable. Empty string if not applicable.
            "customDimension11": "",  # This is the catalogue repository where applicable. Empty string if not applicable.
            "customDimension12": "",  # This is the catalogue level where applicable. Empty string if not applicable.
            "customDimension13": "",  # This is the catalogue series where applicable. Empty string if not applicable.
            "customDimension14": "",  # This is the catalogue reference where applicable. Empty string if not applicable.
            "customDimension15": "",  # This is the catalogueDataSource where applicable. Empty string if not applicable.
            "customDimension16": "",  # This is the availability condition category where applicable. Empty string if not applicable.
            "customDimension17": "",  # This is the availability condition where applicable. Empty string if not applicable.
        }

        # Add request-specific data
        # NOTE: Could potentially be added via JS if we want to keep
        # server responses cacheable
        data.update(
            customDimension1="offsite",
            customDimension2="",
        )
        return data


class SearchDataLayerMixin(DataLayerMixin):
    """
    A mixin applied to Search classes to allow them to customise the Google Analytics
    datalayer.
    """

    gtm_content_group: str = "Search"

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        data.update(
            customDimension3=self.__class__.__name__,  # The page type - [Always has a value]
            customDimension8="",  # This is the search bucket. Empty string if not applicable.
            customDimension9="",  # This is the search term. Empty string if not applicable.
            customMetric1=0,  # This is the number of search results returned
            customMetric2=0,  # This is the number of search filters applied
        )
        return data
