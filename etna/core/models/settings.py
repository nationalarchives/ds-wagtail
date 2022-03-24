from django.db import models

from modelcluster.models import ClusterableModel, ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.models import Page

from etna.navigation.models import AbstractMenuItem

__all__ = ["SiteSettings", "MainMenuItem"]


@register_setting(icon="list-ul")
class SiteSettings(BaseSetting, ClusterableModel):
    panels = [
        InlinePanel(
            "main_menu_items_rel",
            heading="main menu items",
            label="item",
            min_num=1,
            max_num=6,
        ),
    ]

    @classmethod
    def base_queryset(cls):
        """
        For efficiency, prefetch menu items and their related pages when
        looking up site settings from the database.
        """
        return (
            super()
            .base_queryset()
            .prefetch_related(
                "main_menu_items_rel",
                models.Prefetch(
                    "main_menu_items_rel__page",
                    queryset=Page.objects.all().annotate_site_root_state(),
                ),
            )
        )

    @classmethod
    def for_request(cls, request):
        """
        Extends ``BaseSetting.for_request()`` to call
        ``MenuItem.bind_to_request()`` for all menu items
        """
        obj = super().for_request(request)
        obj.main_menu_items = [
            item.bind_to_request(request) for item in obj.main_menu_items_rel.all()
        ]
        return obj


class MainMenuItem(AbstractMenuItem):
    settings = ParentalKey(
        "SiteSettings", on_delete=models.CASCADE, related_name="main_menu_items_rel"
    )
    handle = models.SlugField(
        blank=True,
        help_text=(
            "Optionally specify a value that can be used to refer to this "
            "item in menu templates (e.g. to apply icons / css class names). "
            "Once set, you should avoid changing this value."
        ),
    )

    panels = AbstractMenuItem.panels + [FieldPanel("handle")]
