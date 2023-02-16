from typing import Any, Dict

from django.db import models
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.images import get_image_model_string
from wagtailmetadata.models import MetadataPageMixin

from etna.analytics.mixins import DataLayerMixin
from etna.core.cache_control import (
    apply_default_cache_control,
    apply_default_vary_headers,
)

__all__ = [
    "BasePage",
]


@method_decorator(apply_default_vary_headers, name="serve")
@method_decorator(apply_default_cache_control, name="serve")
class BasePage(MetadataPageMixin, DataLayerMixin, Page):
    """
    An abstract base model that is used for all Page models within
    the project. Any common fields, Wagtail overrides or custom
    functionality can be added here.
    """

    teaser_text = models.TextField(
        verbose_name=_("teaser text"),
        help_text=_(
            "A short, enticing description of this page. This will appear in promos and under thumbnails around the site."
        ),
        max_length=160,
    )

    teaser_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # DataLayerMixin overrides
    gtm_content_group = "Page"

    promote_panels = MetadataPageMixin.promote_panels + [
        FieldPanel("teaser_image"),
        FieldPanel("teaser_text"),
    ]

    class Meta:
        abstract = True

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
