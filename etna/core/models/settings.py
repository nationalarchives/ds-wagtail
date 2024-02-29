from django.db import models

from modelcluster.models import ClusterableModel, ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField
from wagtail.models import Page

from etna.navigation.models import AbstractMenuItem

__all__ = ["SiteSettings", "MainMenuItem"]


@register_setting(icon="list-ul")
class SiteSettings(BaseSiteSetting, ClusterableModel):
    beta_banner_standfirst = models.CharField(
        max_length=200,
        default="What does the 'beta' label mean?",
        verbose_name="standfirst",
    )
    beta_banner_link = models.CharField(
        max_length=200, blank=True, verbose_name="link to"
    )
    beta_banner_link_text = models.CharField(
        max_length=200,
        default="Find out more",
        verbose_name="link text",
    )
    beta_banner_text = RichTextField(
        verbose_name="text",
        default=(
            "<p>This beta site contains new services and features currently in development. Many of these features are "
            "works in progress and are being updated regularly. You can help us improve them by providing feedback as you "
            "use the site.</p> "
        ),
    )
    panels = [
        MultiFieldPanel(
            heading="BETA banner",
            children=[
                FieldPanel("beta_banner_standfirst"),
                FieldPanel("beta_banner_text"),
                FieldPanel("beta_banner_link"),
                FieldPanel("beta_banner_link_text"),
            ],
        ),
        InlinePanel(
            "main_menu_items_rel",
            heading="main menu items",
            label="item",
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
