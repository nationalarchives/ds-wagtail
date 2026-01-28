from app.alerts.models import ThemedAlertMixin
from app.core.blocks.links import LinkBlock
from app.core.models import BasePageWithRequiredIntro, HeroImageMixin
from app.core.models.basepage import BasePage
from app.core.models.mixins import SocialMixin
from app.ukgwa.blocks import InformationPageStreamBlock
from app.ukgwa.mixins import FeaturedLinksMixin, SearchMixin, SidebarNavigationMixin
from app.ukgwa.serializers import SubpagesSerializer
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet


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


class UKGWABasePage(ThemedAlertMixin, BasePageWithRequiredIntro):
    """
    Base page for UK Government Web Archive (UKGWA) pages.

    UKGWA pages don't use teaser images, so this class:
    - Customizes promote_panels to hide teaser_image from the admin UI
      (uses BasePage's panel building blocks and omits teaser_image)
    - Overrides api_meta_fields to exclude teaser_image_square from API responses
      (which requires teaser_image to exist)

    The teaser_image field still exists in the database (inherited from BasePage)
    but is not used or exposed for UKGWA pages.

    Adds show_in_menus field which defaults to True for UKGWA pages.
    """

    class Meta:
        abstract = True

    show_in_menus_default = True

    # Custom internal data panel without teaser_image
    _internal_data_panel = MultiFieldPanel(
        [
            FieldPanel("teaser_text"),
            # Omit teaser_image - UKGWA pages don't use it
        ],
        heading="Internal data",
    )

    promote_panels = [
        BasePage._search_engine_panel,
        FieldPanel("show_in_menus"),  # Add below the slug field
        BasePage._short_title_panel,
        _internal_data_panel,
    ] + SocialMixin.promote_panels

    # Compose API meta fields without teaser_image and teaser_image_square
    api_meta_fields = (
        BasePage._base_api_meta_fields
        + [APIField("teaser_text")]
        + SocialMixin._social_base_api_meta_fields
    )

    # Override to hide inherited alert field
    settings_panels = Page.settings_panels + ThemedAlertMixin.settings_panels

    # Override api_fields to exclude alert
    api_fields = BasePageWithRequiredIntro.api_fields + ThemedAlertMixin.api_fields


class UKGWAHomePage(HeroImageMixin, SearchMixin, UKGWABasePage):
    """
    Homepage for UK Government Web Archive site.

    This page requires exactly 2 featured links sections, which is why it uses
    FeaturedLinksSection via InlinePanel rather than FeaturedLinksMixin.
    """

    parent_page_types = ["wagtailcore.Page"]

    content_panels = (
        UKGWABasePage.content_panels
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
        + SearchMixin.api_fields
        + [APIField("featured_links_sections")]
    )

    settings_panels = UKGWABasePage.settings_panels + SearchMixin.settings_panels

    max_count = 1

    class Meta:
        verbose_name = "UKGWA Home Page"


class SectionIndexPage(SearchMixin, UKGWABasePage):
    """
    Index page that returns its direct child pages which have 'show in menus' enabled.
    """

    parent_page_types = ["ukgwa.UKGWAHomePage"]
    subpage_types = ["ukgwa.InformationPage", "ukgwa.ListingPage"]

    @property
    def subpages(self):
        return self.get_children().live().public().in_menu().specific()

    api_fields = (
        UKGWABasePage.api_fields
        + SearchMixin.api_fields
        + [
            APIField("subpages", serializer=SubpagesSerializer()),
        ]
    )
    content_panels = UKGWABasePage.content_panels

    settings_panels = UKGWABasePage.settings_panels + SearchMixin.settings_panels


class InformationPage(FeaturedLinksMixin, SidebarNavigationMixin, UKGWABasePage):

    parent_page_types = ["ukgwa.SectionIndexPage", "ukgwa.ListingPage"]
    subpage_types = []

    body = StreamField(InformationPageStreamBlock, blank=True, null=True)

    search_fields = UKGWABasePage.search_fields + [
        index.SearchField("body"),
    ]

    api_fields = (
        UKGWABasePage.api_fields
        + FeaturedLinksMixin.api_fields
        + SidebarNavigationMixin.api_fields
        + [
            APIField("body"),
        ]
    )
    content_panels = (
        UKGWABasePage.content_panels
        + [
            FieldPanel("body"),
        ]
        + FeaturedLinksMixin.get_featured_links_panels()
    )
    settings_panels = (
        UKGWABasePage.settings_panels + SidebarNavigationMixin.settings_panels
    )


@register_snippet
class ArchiveSearchComponent(models.Model):
    """
    Reusable search component snippet for archive searches.

    Allows editors to create configured search components that can be added to pages via
    the SearchMixin.
    """

    class ArchiveTypes(models.TextChoices):
        WEB = "web", "Web Archive"
        SOCIAL = "social", "Social Media Archive"

    name = models.CharField(
        verbose_name=_("name"),
        max_length=255,
        help_text=_(
            "Internal name to identify this search component (not shown to users)"
        ),
    )
    heading = models.CharField(
        verbose_name=_("heading"),
        max_length=255,
        help_text=_(
            "The heading text displayed above the search bar (e.g. 'Web Archive Search')"
        ),
    )
    help_text = models.TextField(
        verbose_name=_("help text"),
        blank=True,
        help_text=_(
            "Optional guidance text displayed below the search box to help users understand what they can search for"
        ),
    )
    button_text = models.CharField(
        verbose_name=_("button text"),
        max_length=50,
        default="Search",
        help_text=_("The text displayed on the search button"),
    )
    archive_type = models.CharField(
        verbose_name=_("archive type"),
        max_length=20,
        choices=ArchiveTypes.choices,
        help_text=_(
            "Select whether this component searches the Web Archive or Social Media Archive"
        ),
    )

    panels = [
        FieldPanel("name"),  # Wagtail use only
        FieldPanel("heading"),
        FieldPanel("help_text"),
        FieldPanel("button_text"),
        FieldPanel("archive_type"),
    ]

    api_fields = [
        APIField("heading"),
        APIField("help_text"),
        APIField("button_text"),
        APIField("archive_type"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Archive Search Component")
        verbose_name_plural = _("Archive Search Components")


class ListingPage(UKGWABasePage):
    parent_page_types = ["ukgwa.SectionIndexPage"]
    subpage_types = ["ukgwa.InformationPage"]
