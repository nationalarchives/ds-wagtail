from app.alerts.models import ThemedAlertMixin
from app.core.blocks.links import LinkBlock
from app.core.models import BasePageWithRequiredIntro, HeroImageMixin
from app.core.models.basepage import BasePage
from app.core.models.mixins import SocialMixin
from app.ukgwa.blocks import InformationPageStreamBlock
from app.ukgwa.mixins import FeaturedLinksMixin, SearchMixin
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


class ArchiveRecord(models.Model):
    """
    Archive record from external JSON source.

    - Synced via management command from external archive data.
    - Includes computed fields for efficient filtering and sorting.
    """

    # Unique identifier from source
    wam_id = models.IntegerField(
        unique=True,
        db_index=True,
        help_text=_("WAM database ID (unique identifier)"),
    )

    # Core fields
    profile_name = models.TextField(
        help_text=_("Display name of the archive record"),
    )
    record_url = models.TextField(
        help_text=_("Original URL of the archived site"),
    )
    archive_link = models.TextField(
        help_text=_("Link to the archived version"),
    )
    domain_type = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Type of domain (e.g., Domain, SocialMedia)"),
    )
    first_capture_display = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Human-readable first capture date"),
    )
    latest_capture_display = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Human-readable latest capture date"),
    )
    ongoing = models.BooleanField(
        default=False,
        help_text=_("Whether archiving is ongoing"),
    )
    description = models.TextField(
        help_text=_("Description of archive record"),
    )

    # Computed fields for sorting and filtering
    sort_name = models.TextField(
        db_index=True,
        help_text=_("Normalized name for sorting (strips 'The' prefix)"),
    )
    first_character = models.CharField(
        max_length=5,
        db_index=True,
        help_text=_("First character for navigation: a-z, 0-9, or 'other' for symbols"),
    )

    # Hash for change detection
    record_hash = models.CharField(
        max_length=32,
        help_text=_("MD5 hash of record data for change detection"),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Archive record")
        verbose_name_plural = _("Archive records")
        ordering = ["sort_name"]
        indexes = [
            models.Index(fields=["first_character", "sort_name"]),
        ]

    def __str__(self):
        return self.profile_name

    @classmethod
    def get_available_letters(cls):
        """
        Get list of characters that have records.
        Returns sorted list: digits (0-9), then letters (a-z), then 'other' at the end.
        Note: 'other' represents symbols/special characters.
        """
        # Get unique first_character values
        letters = set(cls.objects.values_list("first_character", flat=True))

        # Custom sort: digits (0-9), then letters (a-z), then 'other' at the end
        def sort_key(char):
            if char == "other":
                return (2, "")  # 'other' last
            elif char.isdigit():
                return (0, char)  # Digits first
            elif char.isalpha():
                return (1, char)  # Letters second
            else:
                return (2, char)  # Any unexpected value

        return sorted(letters, key=sort_key)

    @classmethod
    def get_records_for_letter(cls, letter):
        """
        Get all records for a specific letter, ordered by sort name. Letter should be
        lowercase (a-z), digit (0-9), or 'other'.
        """
        # Normalize to lowercase for letters, keep digits and 'other' as-is
        normalized = letter.lower() if letter and letter.isalpha() else letter
        return cls.objects.filter(first_character=normalized).order_by("sort_name")


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


class InformationPage(FeaturedLinksMixin, UKGWABasePage):

    parent_page_types = ["ukgwa.SectionIndexPage", "ukgwa.ListingPage"]
    subpage_types = []

    body = StreamField(InformationPageStreamBlock, blank=True, null=True)

    search_fields = UKGWABasePage.search_fields + [
        index.SearchField("body"),
    ]

    api_fields = (
        UKGWABasePage.api_fields
        + FeaturedLinksMixin.api_fields
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


class AtoZArchivePage(UKGWABasePage):
    """
    A-Z Archive index page.

    - Displays an alphabetical/numerical index of archive records.
    - Records are filtered via the separate archive records API endpoint.
    """

    parent_page_types = ["ukgwa.UKGWAHomePage"]
    subpage_types = []

    max_count = 1

    @property
    def available_characters(self):
        """
        Get list of characters that have archive records.

        Returns sorted list: ['0', '1', ..., '9', 'a', 'b', ..., 'z', 'other']
        """
        return ArchiveRecord.get_available_letters()

    api_fields = (
        UKGWABasePage.api_fields
        + SearchMixin.api_fields
        + [
            APIField("available_characters"),
        ]
    )

    content_panels = UKGWABasePage.content_panels

    class Meta:
        verbose_name = "A-Z Archive Page"


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
