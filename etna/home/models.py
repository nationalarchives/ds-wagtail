from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from etna.core.models import BasePage

from ..alerts.models import AlertMixin
from .blocks import HomePageStreamBlock
from ..core.blocks.cta import FeaturedCollectionBlock


class HomePage(AlertMixin, BasePage):
    sub_heading = models.CharField(max_length=255, blank=False,
                                   default="Discover some of the most important and unusual records from over 1000 "
                                           "years of history.")
    featured_insight = models.ForeignKey(
        "insights.InsightsPage", blank=True, null=True, on_delete=models.SET_NULL
    )
    body = StreamField(HomePageStreamBlock, blank=True, null=True, use_json_field=True)
    featured_collections = StreamField(
        [("featuredcollection", FeaturedCollectionBlock())],
        blank=True,
        null=True,
        use_json_field=True,
    )
    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("body"),
        FieldPanel("featured_insight"),
        FieldPanel("featured_collections"),
    ]
    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels

    def get_context(self, request):
        context = super().get_context(request)
        insights_pages = self.get_children().live().specific()
        context["insights_pages"] = insights_pages
        context["etna_index_pages"] = [
            {
                "title": "Collection Explorer",
                "introduction": (
                    "A new way to discover collections at The National Archives, "
                    "through records hand-picked by our experts."
                ),
                "url": "#",
            },
            {
                "title": "Collection Insights",
                "introduction": (
                    "Learn about the people, themes and events featured in our records, "
                    "told through words, pictures and audio - discover the human stories behind the collection."
                ),
                "url": "#",
            },
            {
                "title": "Collection Details",
                "introduction": "View and navigate records from The National Archives catalogue.",
                "url": "#",
            },
        ]

        return context
