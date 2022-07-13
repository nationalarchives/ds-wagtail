from typing import Any, Dict

from django.http import HttpRequest
from django.utils.decorators import method_decorator

from wagtail.core.models import Page

from etna.analytics.mixins import DataLayerMixin
from etna.core.cache_control import (
    apply_default_cache_control,
    apply_default_vary_headers,
)

__all__ = [
    "BasePage",
]


GTM_CONTENT_GROUPS = {
    "home": "Homepage",
    "insights": "Insights",
    "collections": "Explorer",
}


@method_decorator(apply_default_vary_headers, name="serve")
@method_decorator(apply_default_cache_control, name="serve")
class BasePage(DataLayerMixin, Page):
    """
    An abstract base model that is used for all Page models within
    the project. Any common fields, Wagtail overrides or custom
    functionality can be added here.
    """

    class Meta:
        abstract = True

    def get_gtm_content_group(self) -> str:
        """
        Overrides DataLayerMixin.get_gtm_content_group() to
        derive a string from the model's app label.
        """
        app_label = self._meta.label.split(".")[0]
        return GTM_CONTENT_GROUPS.get(app_label, self.title)

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Return values that should be included in the Google Analytics datalayer
        when rendering this page.

        Override this method on subclasses to add data that is relevant to a
        specific page type.
        """
        data = super().get_datalayer_data(request)
        data.update(customDimension3=self._meta.verbose_name)
        return data
