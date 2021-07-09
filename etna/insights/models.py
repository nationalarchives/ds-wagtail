from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel


from .blocks import InsightsPageStreamBlock


class InsightsIndexPage(Page):
    """InsightsIndexPage

    This page lists the InsightsPage objects that are children of this page.
    """
    introduction = models.CharField(max_length=200, blank=False)

    def get_context(self, request):
        context = super().get_context(request)
        insights_pages = self.get_children().live().public().specific()
        context['insights_pages'] = insights_pages
        return context

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]

    subpage_types = ['insights.InsightsPage']


class InsightsPage(Page):
    """InsightsPage

    The InsightsPage model.
    """
    introduction = models.CharField(max_length=200, blank=False)
    body = StreamField(InsightsPageStreamBlock, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        StreamFieldPanel('body'),
    ]

    parent_page_types = ['insights.InsightsIndexPage']
    subpage_types = []
