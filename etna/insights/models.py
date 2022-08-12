from typing import Any, Dict, Tuple

from django.db import models
from django.http import HttpRequest
from django.utils.functional import cached_property

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from taggit.models import ItemBase, TagBase

from etna.core.models import BasePage, ContentWarningMixin

from ..heroes.models import HeroImageMixin
from ..teasers.models import TeaserImageMixin
from .blocks import FeaturedCollectionBlock, InsightsPageStreamBlock


class InsightsIndexPage(TeaserImageMixin, BasePage):
    """InsightsIndexPage

    This page lists the InsightsPage objects that are children of this page.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    featured_insight = models.ForeignKey(
        "insights.InsightsPage", blank=True, null=True, on_delete=models.SET_NULL
    )
    featured_collections = StreamField(
        [("featuredcollection", FeaturedCollectionBlock())],
        blank=True,
        null=True,
        use_json_field=True,
    )

    def get_context(self, request):
        featuredcollections = []
        context = super().get_context(request)
        insights_pages = self.get_children().live().specific()
        context["insights_pages"] = insights_pages
        for block in self.featured_collections:
            for insight in block.value["items"].bound_blocks:
                featuredcollections.append(insight.value)
        context["featuredcollections"] = featuredcollections
        return context

    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("featured_insight"),
        FieldPanel("featured_collections"),
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


class InsightsPage(HeroImageMixin, TeaserImageMixin, ContentWarningMixin, BasePage):
    """InsightsPage

    The InsightsPage model.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(
        InsightsPageStreamBlock, blank=True, null=True, use_json_field=True
    )
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
    insight_tag_names = models.TextField(editable=False)
    tags = ClusterTaggableManager(through=TaggedInsights, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("insight_tag_names"),
    ]

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        if self.topic:
            data["customDimension4"] = self.topic.title
        if self.insight_tag_names:
            data["customDimension6"] = ";".join(self.insight_tag_names.split("\n"))
        if self.time_period:
            data["customDimension7"] = self.time_period.title
        return data

    def save(self, *args, **kwargs):
        """
        Overrides Page.save() to ensure 'insight_tag_names' always reflects the tags() value
        """
        if (
            "update_fields" not in kwargs
            or "insight_tag_names" in kwargs["update_fields"]
        ):
            self.insight_tag_names = "\n".join(t.name for t in self.tags.all())
        super().save(*args, **kwargs)

    @cached_property
    def similar_items(self) -> Tuple["InsightsPage"]:
        """
        Returns a maximum of three InsightsPages that are tagged with at least
        one of the same InsightsTags. Items should be ordered by the number
        of tags they have in common.
        """
        if not self.insight_tag_names:
            # Avoid unncecssary lookups
            return ()

        tag_ids = self.tagged_items.values_list("tag_id", flat=True)
        if not tag_ids:
            # Avoid unncecssary lookups
            return ()

        # Identify 'other' live pages with tags in common
        tag_match_ids = (
            InsightsPage.objects.live()
            .not_page(self)
            .filter(tagged_items__tag_id__in=tag_ids)
            .values_list("id", flat=True)
            .distinct()
        )
        if not tag_match_ids:
            # Avoid unncecssary lookups
            return ()

        # Use search() to prioritise items with the highest number of matches
        return tuple(
            InsightsPage.objects.filter(id__in=tag_match_ids).search(
                self.insight_tag_names,
                fields=["insight_tag_names"],
                operator="or",
            )[:3]
        )

    @cached_property
    def latest_items(self) -> Tuple["InsightsPage"]:
        """
        Return the three most recently published InsightsPages,
        excluding this object.
        """
        similarqueryset = list(self.similar_items)

        latestqueryset = list(
            InsightsPage.objects.live()
            .not_page(self)
            .select_related("hero_image", "topic", "time_period")
            .order_by("-first_published_at")
        )
        filterlatestpages= [page for page in latestqueryset if page not in similarqueryset]

        return tuple(filterlatestpages)



    content_panels = (
        BasePage.content_panels
        + HeroImageMixin.content_panels
        + [
            FieldPanel("sub_heading"),
            FieldPanel("topic"),
            FieldPanel("time_period"),
            FieldPanel("tags"),
            MultiFieldPanel(
                [
                    FieldPanel("display_content_warning"),
                    FieldPanel("custom_warning_text"),
                ],
                heading="Content Warning Options",
                classname="collapsible collapsed",
            ),
            FieldPanel("body"),
        ]
    )

    promote_panels = BasePage.promote_panels + TeaserImageMixin.promote_panels

    parent_page_types = ["insights.InsightsIndexPage"]
    subpage_types = []
