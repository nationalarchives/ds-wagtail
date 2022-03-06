from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.snippets.models import register_snippet

from taggit.models import ItemBase, TagBase

from etna.core.models import BasePage

from ..heroes.models import HeroImageMixin
from ..teasers.models import TeaserImageMixin
from .blocks import InsightsIndexPageStreamBlock, InsightsPageStreamBlock


class InsightsIndexPage(TeaserImageMixin, BasePage):
    """InsightsIndexPage

    This page lists the InsightsPage objects that are children of this page.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(InsightsIndexPageStreamBlock, blank=True, null=True)
    featured_insight = models.ForeignKey(
        "insights.InsightsPage", blank=True, null=True, on_delete=models.SET_NULL
    )

    def get_context(self, request):
        context = super().get_context(request)
        insights_pages = self.get_children().live().specific()
        context["insights_pages"] = insights_pages
        return context

    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        StreamFieldPanel("body"),
    ]
    promote_panels = BasePage.promote_panels + TeaserImageMixin.promote_panels

    subpage_types = ["insights.InsightsPage"]


@register_snippet
class InsightsTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "insights tag"
        verbose_name_plural = "insights tags"


class TaggedInsights(ItemBase):
    tag = models.ForeignKey(
        InsightsTag, related_name="tagged_insights", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="insights.InsightsPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class InsightsPage(HeroImageMixin, TeaserImageMixin, BasePage):
    """InsightsPage

    The InsightsPage model.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(InsightsPageStreamBlock, blank=True, null=True)
    topic = models.ForeignKey(
        "collections.TopicExplorerPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    time_period = models.ForeignKey(
        "collections.TimePeriodExplorerPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    tags = ClusterTaggableManager(through=TaggedInsights, blank=True)
    content_panels = (
        BasePage.content_panels
        + HeroImageMixin.content_panels
        + [
            FieldPanel("sub_heading"),
            FieldPanel("topic"),
            FieldPanel("time_period"),
            FieldPanel("tags"),
            StreamFieldPanel("body"),
        ]
    )

    promote_panels = BasePage.promote_panels + TeaserImageMixin.promote_panels

    parent_page_types = ["insights.InsightsIndexPage"]
    subpage_types = []
