from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    PageChooserPanel,
    MultiFieldPanel,
)
from wagtail.api import APIField


class FeaturedPage:
    def get_chooser(**kwargs) -> PageChooserPanel:
        return PageChooserPanel(**kwargs)

    def get_field(null: bool = True, blank: bool = True, verbose_name: str = "featured page", related_name: str = "+", on_delete=models.SET_NULL) -> models.ForeignKey:
        return models.ForeignKey(
            "wagtailcore.Page",
            null=null,
            blank=blank,
            on_delete=on_delete,
            related_name=related_name,
            verbose_name=verbose_name,
        )

    def get_api_field(name: str = "featured_page", serializer = None) -> APIField:
        return APIField(name=name, serializer=serializer)

