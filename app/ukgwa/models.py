from wagtail.api import APIField

from app.core.models import BasePageWithRequiredIntro, HeroImageMixin
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
