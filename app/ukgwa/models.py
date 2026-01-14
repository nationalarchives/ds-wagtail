import copy

from app.core.blocks.links import LinkBlock
from app.core.models import BasePageWithRequiredIntro, HeroImageMixin
from app.core.models.mixins import SocialMixin
from app.ukgwa.serializers import SubpagesSerializer
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.fields import StreamField


class FeaturedLinksSection(models.Model):
    """
    A featured links section with a heading and exactly 3 links.

    This is specifically used for the UKGWAHomePage which requires 2 featured links
    sections. For pages needing only 1 featured links section, use FeaturedLinksMixin
    instead to avoid unnecessary API nesting.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="featured_links_sections",
    )
    heading = models.CharField(
        verbose_name=_("featured links heading text"),
        max_length=100,
        help_text=_("A short heading for the featured links section"),
    )
    links = StreamField(
        [("link", LinkBlock())],
        verbose_name=_("featured links"),
        min_num=3,
        max_num=3,
        use_json_field=True,
        help_text=_(
            "Contains exactly three links. Each link can be to an internal page or an external URL."
        ),
    )

    panels = [
        FieldPanel("heading"),
        FieldPanel("links"),
    ]

    api_fields = [
        APIField("heading"),
        APIField("links"),
    ]

    class Meta:
        verbose_name = "Featured links section"
        verbose_name_plural = "Featured links sections"


class UKGWABasePage(BasePageWithRequiredIntro):
    """Base page for UKGWA with customized panels"""

    class Meta:
        abstract = True

    show_in_menus_default = True

    base_page_promote_panels = copy.deepcopy(BasePageWithRequiredIntro.promote_panels)
    # Remove teaser_image from the BasePageWithRequiredIntro promote panels
    for panel in base_page_promote_panels:
        if hasattr(panel, "heading") and panel.heading == "Internal data":
            panel.children = [
                child
                for child in panel.children
                if getattr(child, "field_name", None) != "teaser_image"
            ]

    promote_panels = (
        base_page_promote_panels[:1]
        + [FieldPanel("show_in_menus")]  # Add below the slug field
        + base_page_promote_panels[1:]
        + SocialMixin.promote_panels
    )


class UKGWAHomePage(HeroImageMixin, UKGWABasePage):
    """
    Homepage for UK Government Web Archive site.

    This page requires exactly 2 featured links sections, which is why it uses
    FeaturedLinksSection via InlinePanel rather than FeaturedLinksMixin.
    """

    parent_page_types = ["wagtailcore.Page"]

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + HeroImageMixin.content_panels
        + [
            InlinePanel(
                "featured_links_sections",
                label=_("Featured links section"),
                min_num=2,
                max_num=2,
                help_text=_("Add exactly 2 featured links sections to the homepage"),
            )
        ]
    )

    api_fields = (
        UKGWABasePage.api_fields
        + HeroImageMixin.api_fields
        + [APIField("featured_links_sections")]
    )

    max_count = 1

    class Meta:
        verbose_name = "UKGWA Home Page"


class SectionIndexPage(UKGWABasePage):
    """
    Index page that returns its direct child pages which have 'show in menus' enabled.
    """

    # TODO: Uncomment when other subpage types have been added and can be used for
    # testing
    #
    # parent_page_types = ["ukgwa.UKGWAHomePage"]
    subpage_types = ["ukgwa.SectionIndexPage"]

    @property
    def subpages(self):
        return self.get_children().live().public().in_menu().specific()

    api_fields = UKGWABasePage.api_fields + [
        APIField("subpages", serializer=SubpagesSerializer()),
    ]
    content_panels = UKGWABasePage.content_panels
