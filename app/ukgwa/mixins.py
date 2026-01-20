from app.core.blocks.links import LinkBlock
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField


class FeaturedLinksMixin(models.Model):
    """
    Add a single featured links section to a page.

    For pages requiring multiple featured links sections (like UKGWAHomePage which needs
    2), use the FeaturedLinksSection class with an InlinePanel instead.
    """

    featured_links_heading = models.CharField(
        verbose_name=_("featured links heading text"),
        max_length=100,
        help_text="A short heading for the featured links section",
    )
    featured_links = StreamField(
        [("link", LinkBlock())],
        verbose_name=_("featured links"),
        min_num=3,
        max_num=3,
        use_json_field=True,
        help_text=_(
            "Contains exactly three links. Each link can be to an internal page or an external URL."
        ),
    )

    api_fields = [
        APIField("featured_links_heading"),
        APIField("featured_links"),
    ]

    class Meta:
        abstract = True

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


class SidebarNavigationMixin(models.Model):
    """Mixin to add section navigation sidebar to pages."""

    show_sidebar_navigation = models.BooleanField(
        default=True,
        help_text="Show a navigation sidebar of sibling pages within this section",
    )

    @property
    def sidebar_navigation(self):
        """Return section navigation data if enabled and parent is a SectionIndexPage."""
        if not self.show_sidebar_navigation:
            return None

        parent = self.get_parent().specific

        # Check if parent is a SectionIndexPage using lazy model name check
        if not parent or parent._meta.model_name != "sectionindexpage":
            return None

        # Check if parent has subpages
        if not hasattr(parent, "subpages") or not parent.subpages:
            return None

        return {
            "parent_page_title": parent.title,
            "subpages": [
                {
                    "text": page.title,
                    "href": page.url,
                    "is_current": page.id == self.id,
                }
                for page in parent.subpages
            ],
        }

    class Meta:
        abstract = True

    settings_panels = [
        FieldPanel("show_sidebar_navigation"),
    ]

    api_fields = [
        APIField("sidebar_navigation"),
    ]
