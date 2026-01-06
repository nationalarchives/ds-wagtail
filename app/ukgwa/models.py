from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.search import index

from app.core.models import BasePageWithRequiredIntro, HeroImageMixin
from app.ukgwa.blocks import InformationPageStreamBlock
from app.ukgwa.mixins import FeaturedLinksMixin


class UKGWAHomePage(FeaturedLinksMixin, HeroImageMixin, BasePageWithRequiredIntro):
    """
    Homepage for UK Government Web Archive site.
    Has different featured link structure compared to TNA's HomePage.
    """

    parent_page_types = ["wagtailcore.Page"]

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + FeaturedLinksMixin.get_featured_links_panels()
    )

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + HeroImageMixin.api_fields
        + FeaturedLinksMixin.api_fields
    )

    max_count = 1

    class Meta:
        verbose_name = "UKGWA Home Page"


class InformationPage(FeaturedLinksMixin, BasePageWithRequiredIntro):
    body = StreamField(InformationPageStreamBlock())

    search_fields = BasePageWithRequiredIntro.search_fields + [
        index.SearchField("body"),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + FeaturedLinksMixin.api_fields
        + [
            APIField("body"),
        ]
    )
    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + [
            FieldPanel("body"),
        ]
        + FeaturedLinksMixin.get_featured_links_panels()
    )
