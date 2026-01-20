from app.core.blocks.links import LinkBlock
from app.ukgwa.serializers import ArchiveSearchComponentSerializer
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
