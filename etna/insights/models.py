from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from ..heroes.models import HeroImageMixin
from ..teasers.models import TeaserImageMixin
from .blocks import InsightsIndexPageStreamBlock, InsightsPageStreamBlock


class InsightsIndexPage(TeaserImageMixin, Page):
    """InsightsIndexPage

    This page lists the InsightsPage objects that are children of this page.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(InsightsIndexPageStreamBlock, blank=True, null=True)

    def get_context(self, request):
        context = super().get_context(request)
        insights_pages = self.get_children().live().specific()
        context["insights_pages"] = insights_pages
        return context

    content_panels = Page.content_panels + [
        FieldPanel("sub_heading"),
        StreamFieldPanel("body"),
    ]
    promote_panels = Page.promote_panels + TeaserImageMixin.promote_panels

    subpage_types = ["insights.InsightsPage"]


class InsightsPage(HeroImageMixin, TeaserImageMixin, Page):
    """InsightsPage

    The InsightsPage model.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(InsightsPageStreamBlock, blank=True, null=True)

    content_panels = (
        Page.content_panels
        + HeroImageMixin.content_panels
        + [
            FieldPanel("sub_heading"),
            StreamFieldPanel("body"),
        ]
    )

    promote_panels = Page.promote_panels + TeaserImageMixin.promote_panels

    parent_page_types = ["insights.InsightsIndexPage"]
    subpage_types = []
