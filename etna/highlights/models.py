from cProfile import label
from typing import Any, Dict, Tuple
from typing_extensions import Required
 
from django.db import models
from django.http import HttpRequest
from django.utils.functional import cached_property
 
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.models import Page, Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet
 
from taggit.models import ItemBase, TagBase
from wagtailmetadata.models import MetadataPageMixin
 
from etna.core.models import BasePage, ContentWarningMixin
from etna.records.blocks import RecordChooserBlock

from .blocks import HighlightsRecordBlock
from ..heroes.models import HeroImageMixin
from ..teasers.models import TeaserImageMixin
from ..collections.models import TaggedTimePeriods, TaggedTopics


@register_snippet
class Highlights(models.Model):
    title = models.CharField(max_length=255, blank=False, null=True)

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    body = StreamField([
        ('record_info', HighlightsRecordBlock()),
    ], 
    block_counts={
        'record_info': {'min_num': 1, 'max_num': 1},
    }, 
    use_json_field=True,
    null=True,
    )

    closer_look = models.ForeignKey(
        "highlights.CloserLookPage", blank=True, null=True, on_delete=models.SET_NULL
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('image'),
        FieldPanel('body'),
        FieldPanel('closer_look'),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "highlight"
        verbose_name_plural = "highlights"



class HighlightsGalleryPage(BasePage):
    """HighlightsGalleryPage
 
    This page is used to display highlights, which can have Closer Look
    pages attached to them.
    """
    standfirst = models.CharField(max_length=250, blank = False, null=True)
    featured_insight = models.ForeignKey(
        "insights.InsightsPage", blank=True, null=True, on_delete=models.SET_NULL
    )
   
 
    topic_tags = ClusterTaggableManager(through="collections.TaggedTopics", blank=True, verbose_name="Topic Tags")
    time_period_tags = ClusterTaggableManager(through="collections.TaggedTimePeriods", blank=True, verbose_name="Time Period Tags")
   
    content_panels = BasePage.content_panels + [
        FieldPanel("standfirst"),
        FieldPanel("featured_insight"),
        InlinePanel("highlights_gallery", heading="Highlights Gallery", label="Highlight", min_num=1),
        MultiFieldPanel(
            [
                FieldPanel("topic_tags"),
                FieldPanel("time_period_tags"),
            ],
            heading="Tags",
        ),
    ]
 
    parent_page_types = ["collections.ExplorerIndexPage"]
 

class HighlightsGalleryItem(Orderable):
    page = ParentalKey(HighlightsGalleryPage, on_delete=models.CASCADE, related_name='highlights_gallery')
    highlight = models.ForeignKey(
        "highlights.Highlights", blank=False, null=True, on_delete=models.SET_NULL
    )

    class Meta(Orderable.Meta):
        verbose_name = "highlight"

    panels = [
        FieldPanel('highlight'),
    ]
 


class CloserLookPage(BasePage, ContentWarningMixin):
    """CloserLookPage
 
    This page is ______.
    """
    
    topic = models.ForeignKey(
        "collections.TopicExplorerPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Promoted Topic",
    )
    time_period = models.ForeignKey(
        "collections.TimePeriodExplorerPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Promoted Time Period",
    )

    body = StreamField([
        ('record_info', HighlightsRecordBlock()),
    ], 
    block_counts={
        'record_info': {'min_num': 1, 'max_num': 1},
    }, 
    use_json_field=True,
    null=True,
    )

    topic_tags = ClusterTaggableManager(through="collections.TaggedTopics", blank=True, verbose_name="Topic Tags")
    time_period_tags = ClusterTaggableManager(through="collections.TaggedTimePeriods", blank=True, verbose_name="Time Period Tags")

    image_library_link = models.URLField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Link to external image library"
    )

    print_on_demand_link = models.URLField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Link to external print on demand"
    )

    featured_insight = models.ForeignKey(
        "insights.InsightsPage",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Featured insight"
    )

    related_records = models.ForeignKey(
        "highlights.HighlightsGalleryPage",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Related records"
    )

    

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
                [
                    FieldPanel("display_content_warning"),
                    FieldPanel("custom_warning_text"),
                ],
                heading="Content Warning Options",
                classname="collapsible collapsed",
            ),
        InlinePanel("image_gallery", heading="Image Gallery", label="Gallery Image", min_num=1, max_num=6),
        FieldPanel("body"),
        FieldPanel("featured_insight"),
        FieldPanel("related_records"),
        FieldPanel("image_library_link"),
        FieldPanel("print_on_demand_link"),
        MultiFieldPanel(
                [
                    FieldPanel("topic_tags"),
                    FieldPanel("time_period_tags"),
                ],
                heading="Tags",
            ),
        MultiFieldPanel(
            [
                FieldPanel("topic"),
                FieldPanel("time_period"),
            ],
            heading="Topic and Time Periods"
        ),
    ]
 
 
    parent_page_types = ["collections.ExplorerIndexPage"]
    subpage_types = []


class CloserLookGalleryImage(Orderable):
    page = ParentalKey(CloserLookPage, on_delete=models.CASCADE, related_name='image_gallery')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    alt_text = models.CharField(
        max_length=100,
        help_text="Alt text for the image",
        null=True,
        blank=False,
    )
    sensitive_image = models.BooleanField(
        help_text="Apply the sensitive image filter to this image",
        default=False,
    )
    caption = models.CharField(
        max_length=100,
        help_text="A caption for the image",
        null=True,
        blank=True,
    )
    transcription = models.TextField(
        max_length=400, 
        help_text="A transcription of the image",
        null=True,
        blank=True,
    )
    translation_text = models.TextField(
        max_length=400,
        help_text="A translation of the transcription",
        null=True,
        blank=True,
    )
    translation_header = models.CharField(
        max_length=50,
        help_text="Header for the translation",
        null=True,
        blank=True,
    )

    class Meta(Orderable.Meta):
        verbose_name = "gallery image"

    panels = [
        FieldPanel('image'),
        FieldPanel('alt_text'),
        FieldPanel('sensitive_image'),
        FieldPanel('caption'),
        MultiFieldPanel(
            [
                FieldPanel('transcription'),
                MultiFieldPanel(
                [
                    FieldPanel("translation_header"),
                    FieldPanel('translation_text'),
                ],
                heading="Translation"
            ),
            ],
            heading="Translation and Transcription",
        ),
    ]