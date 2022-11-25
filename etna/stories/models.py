from datetime import datetime, timedelta
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
from wagtailmetadata.models import MetadataPageMixin

from etna.core.models import BasePage, ContentWarningMixin

from ..heroes.models import HeroImageMixin
from ..teasers.models import TeaserImageMixin
from .blocks import FeaturedCollectionBlock, StoriesPageStreamBlock


class StoriesIndexPage(TeaserImageMixin, MetadataPageMixin, BasePage):
    """StoriesIndexPage

    This page lists the StoriesPage objects that are children of this page.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    featured_story = models.ForeignKey(
        "stories.StoriesPage", blank=True, null=True, on_delete=models.SET_NULL
    )
    featured_pages = StreamField(
        [("featuredpages", FeaturedCollectionBlock())],
        blank=True,
        null=True,
        use_json_field=True,
    )

    new_label_end_date = datetime.now() - timedelta(days=21)

    def get_context(self, request):
        context = super().get_context(request)
        Stories_pages = self.get_children().public().live().specific()
        context["Stories_pages"] = Stories_pages
        return context

    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("featured_story"),
        FieldPanel("featured_pages"),
    ]

    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels

    subpage_types = ["stories.StoriesPage"]


@register_snippet
class StoriesTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "stories tag"
        verbose_name_plural = "stories tags"


class TaggedStories(ItemBase):
    tag = models.ForeignKey(
        StoriesTag, related_name="tagged_Stories", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="stories.StoriesPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class StoriesPage(
    HeroImageMixin, TeaserImageMixin, ContentWarningMixin, MetadataPageMixin, BasePage
):
    """StoriesPage

    The StoriesPage model.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(
        StoriesPageStreamBlock, blank=True, null=True, use_json_field=True
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
    story_tag_names = models.TextField(editable=False)
    tags = ClusterTaggableManager(through=TaggedStories, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("story_tag_names"),
    ]

    new_label_end_date = datetime.now() - timedelta(days=21)

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        if self.topic:
            data["customDimension4"] = self.topic.title
        if self.story_tag_names:
            data["customDimension6"] = ";".join(self.story_tag_names.split("\n"))
        if self.time_period:
            data["customDimension7"] = self.time_period.title
        return data

    def save(self, *args, **kwargs):
        """
        Overrides Page.save() to ensure 'story_tag_names' always reflects the tags() value
        """
        if (
            "update_fields" not in kwargs
            or "story_tag_names" in kwargs["update_fields"]
        ):
            self.story_tag_names = "\n".join(t.name for t in self.tags.all())
        super().save(*args, **kwargs)

    @cached_property
    def similar_items(self) -> Tuple["StoriesPage"]:
        """
        Returns a maximum of three StoriesPages that are tagged with at least
        one of the same StoriesTags. Items should be ordered by the number
        of tags they have in common.
        """
        if not self.story_tag_names:
            # Avoid unncecssary lookups
            return ()

        tag_ids = self.tagged_items.values_list("tag_id", flat=True)
        if not tag_ids:
            # Avoid unncecssary lookups
            return ()

        # Identify 'other' live pages with tags in common
        tag_match_ids = (
            StoriesPage.objects.public()
            .live()
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
            StoriesPage.objects.filter(id__in=tag_match_ids).search(
                self.story_tag_names,
                fields=["story_tag_names"],
                operator="or",
            )[:3]
        )

    @cached_property
    def latest_items(self) -> Tuple["StoriesPage"]:
        """
        Return the three most recently published StoriesPages,
        excluding this object.
        """
        similarqueryset = list(self.similar_items)

        latestqueryset = list(
            StoriesPage.objects.public()
            .live()
            .not_page(self)
            .select_related("hero_image", "topic", "time_period")
            .order_by("-first_published_at")
        )
        filterlatestpages = [
            page for page in latestqueryset if page not in similarqueryset
        ]

        return tuple(filterlatestpages[:3])

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

    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels

    parent_page_types = ["stories.StoriesIndexPage"]
    subpage_types = []
