from app.core.blocks.links import LinkBlock
from app.core.models import BasePageWithRequiredIntro, HeroImageMixin
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


class UKGWAHomePage(HeroImageMixin, BasePageWithRequiredIntro):
    """
    Homepage for UK Government Web Archive site.

    This page requires exactly 2 featured links sections, which is why it uses
    FeaturedLinksSection via InlinePanel rather than FeaturedLinksMixin.
    """

    parent_page_types = ["wagtailcore.Page"]

    content_panels = BasePageWithRequiredIntro.content_panels + [
        InlinePanel(
            "featured_links_sections",
            label=_("Featured links section"),
            min_num=2,
            max_num=2,
            help_text=_("Add exactly 2 featured links sections to the homepage"),
        )
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + HeroImageMixin.api_fields
        + [APIField("featured_links_sections")]
    )

    max_count = 1

    class Meta:
        verbose_name = "UKGWA Home Page"
