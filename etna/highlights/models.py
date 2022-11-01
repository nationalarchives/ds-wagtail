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
from etna.core.blocks.paragraph import ParagraphBlock
 
from etna.core.models import BasePage, ContentWarningMixin
from etna.insights.blocks import FeaturedRecordBlock
from etna.records.blocks import RecordChooserBlock

from ..heroes.models import HeroImageMixin
from ..teasers.models import TeaserImageMixin



@register_snippet
class Highlights(models.Model):
    title = models.CharField(max_length=255, blank=False, null=True)
    short_description = models.CharField(max_length=200, blank=False, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    date = models.CharField(max_length=20)

    panels = [
        FieldPanel('title'),
        FieldPanel('short_description'),
        FieldPanel('image'),
        FieldPanel('date'),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "highlight"
        verbose_name_plural = "highlights"



class HighlightsGalleryPage(BasePage):
    """HighlightsGalleryPage
 
    This page is ______.
    """
    standfirst = models.CharField(max_length=250, blank = False, null=True)
    #highlights_gallery = multi chooser of highlights
    #featured_collections = StreamField(
    #     [("featuredcollection", FeaturedCollectionBlock())],
    #     blank=True,
    #     null=True,
    #     use_json_field=True,
    # )
    featured_insight = models.ForeignKey(
        "insights.InsightsPage", blank=True, null=True, on_delete=models.SET_NULL
    )
    highlight = models.ForeignKey(
        "highlights.Highlights", blank=True, null=True, on_delete=models.SET_NULL
    )
 
    # highlight_tag_names = models.TextField(editable=False)
    # tags = ClusterTaggableManager(through=TaggedHighlights, blank=True)
 
    # search_fields = Page.search_fields + [
    #     index.SearchField("highlight_tag_names"),
    # ]
 
    # def save(self, *args, **kwargs):
    #     """
    #     Overrides Page.save() to ensure 'highlight_tag_names' always reflects the tags() value
    #     """
    #     if (
    #         "update_fields" not in kwargs
    #         or "highlight_tag_names" in kwargs["update_fields"]
    #     ):
    #         self.highlight_tag_names = "\n".join(t.name for t in self.tags.all())
    #     super().save(*args, **kwargs)
 
   
    content_panels = BasePage.content_panels + [
        FieldPanel("standfirst"),
        FieldPanel("featured_insight"),
        FieldPanel("highlight"),
        #FieldPanel("file"),
        #FieldPanel("record_link"),
        #FieldPanel("date"),
        # FieldPanel("time_period_tags"),
        # FieldPanel("topic_tags"),
    ]
 
    parent_page_types = ["collections.ExplorerIndexPage"]
 
 


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


    featured_insight = models.ForeignKey(
        "insights.InsightsPage",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Featured insight"
    )

    date = models.CharField(
        blank=True,
        null=True,
        max_length=30
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
        FieldPanel("date"),
        FieldPanel("featured_insight"),
        MultiFieldPanel(
            [
                FieldPanel("topic"),
                FieldPanel("time_period"),
            ],
            heading="Topic and Time Periods"
        )
        # FieldPanel("topic_tags"),
        # FieldPanel("time_period_tags"),
        # FieldPanel("image_library_link"), = use this image - use this image how?
        # FieldPanel("print_on_demand_link"), = buy an art print - not done yet?
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