from app.core.blocks.links import LinkBlock
from app.ukgwa.serializers import (
    ArchiveSearchComponentSerializer,
    BookmarkletCTASerializer,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField


class FeaturedLinksMixin(models.Model):
    """
    Add an optional featured links section to a page.

    Either all fields must be populated (heading + exactly 3 links) or none.

    For pages requiring multiple featured links sections (like UKGWAHomePage which needs
    2), use the FeaturedLinksSection class with an InlinePanel instead.
    """

    featured_links_heading = models.CharField(
        verbose_name=_("featured links heading text"),
        max_length=100,
        blank=True,
        help_text="A short heading for the featured links section",
    )
    featured_links = StreamField(
        [("link", LinkBlock())],
        verbose_name=_("featured links"),
        blank=True,
        max_num=3,
        use_json_field=True,
        help_text=_(
            "Exactly three links, or leave empty to hide this section. "
            "Each link can be to an internal page or an external URL."
        ),
    )

    api_fields = [
        APIField("featured_links_heading"),
        APIField("featured_links"),
    ]

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        has_heading = bool(self.featured_links_heading)
        has_links = bool(self.featured_links)
        errors = {}
        if has_links and not has_heading:
            errors["featured_links_heading"] = _(
                "A heading is required when featured links are added."
            )
        if has_heading and not has_links:
            errors["featured_links"] = _(
                "Links are required when a heading is provided."
            )
        if has_links and len(self.featured_links) < 3:
            errors["featured_links"] = _("Please add exactly 3 links.")
        if errors:
            raise ValidationError(errors)

    @staticmethod
    def get_featured_links_panels():
        """Return the panel configuration for featured links"""
        return [
            MultiFieldPanel(
                [
                    FieldPanel("featured_links_heading"),
                    FieldPanel("featured_links"),
                ],
                heading="Featured links",
            )
        ]


class BookmarkletMixin(models.Model):
    """
    Add optional bookmarklet to a page.

    Allows editors to associate a reusable bookmarklet snippet with the page.
    """

    bookmarklet_cta = models.ForeignKey(
        "BookmarkletCTASnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_("Select a bookmarklet CTA snippet to display on this page"),
    )

    api_fields = [
        APIField("bookmarklet_cta", serializer=BookmarkletCTASerializer()),
    ]

    settings_panels = [FieldPanel("bookmarklet_cta")]

    class Meta:
        abstract = True


class SearchMixin(models.Model):
    """
    Add optional archive search functionality to a page.

    Allows editors to associate a reusable ArchiveSearchComponent snippet with
    the page, which can be rendered to provide web archive or social media archive
    search capabilities.
    """

    search_configuration = models.ForeignKey(
        "ArchiveSearchComponent",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_("Select an archive search component to display on this page"),
    )

    api_fields = [
        APIField("search_configuration", serializer=ArchiveSearchComponentSerializer()),
    ]

    settings_panels = [FieldPanel("search_configuration")]

    class Meta:
        abstract = True


class SidebarNavigationMixin(models.Model):
    """Mixin to add section navigation sidebar to pages."""

    show_sidebar_navigation = models.BooleanField(
        default=True,
        help_text=_(
            "Show a navigation sidebar of sibling pages within this section. "
            "Only applies to direct children of a section index."
        ),
    )

    @property
    def sidebar_navigation(self):
        """Return section navigation data if enabled and parent is a SectionIndexPage."""
        if not self.show_sidebar_navigation:
            return None

        parent = self.get_parent().specific

        from app.ukgwa.models import SectionIndexPage

        if not parent or not isinstance(parent, SectionIndexPage):
            return None

        subpages = [
            {
                "text": page.title,
                "href": page.url,
                "is_current": page.id == self.id,
            }
            for page in parent.subpages
        ]
        if not subpages:
            return None
        return {
            "parent_page_title": parent.title,
            "subpages": subpages,
        }

    class Meta:
        abstract = True

    settings_panels = [
        FieldPanel("show_sidebar_navigation"),
    ]

    api_fields = [
        APIField("sidebar_navigation"),
    ]
