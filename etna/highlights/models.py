from typing import Any, Dict, Tuple
from typing_extensions import Required
 
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
from etna.records.blocks import RecordChooserBlock
 
from ..heroes.models import HeroImageMixin
from ..teasers.models import TeaserImageMixin

class Highlights(models.Model):
    title = models.CharField(max_length=255)
    standfirst = models.CharField(max_length=255)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    date = models.CharField(max_length=20)

    panels = [
        FieldPanel('title'),
        FieldPanel('standfirst'),
        FieldPanel('image'),
        FieldPanel('date')
    ]

@register_snippet
class HighlightsTag(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "highlights tag"
        verbose_name_plural = "highlights tags"
 

class TaggedHighlights(ItemBase):
    tag = models.ForeignKey(
        HighlightsTag, related_name="tagged_highlights", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="highlights.HighlightsPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )
 
# class HighlightsIndexPage(BasePage):
#     """HighlightsIndexPage
 
#     Index page to hold Highlights
#     """
#     max_count = 1
#     parent_page_types = ["collections.ExplorerIndexPage"]
#     subpage_types = ["highlights.HighlightsPage"]
 
 
# class HighlightsPage(BasePage):
#     """HighlightsPage
 
#     This page is ______.
#     """
#     #title = models.CharField(max_length=100, blank = False, null=False) #title of the page, e.g. Elton John
#     short_description = models.CharField(max_length=250, blank = False, null=False) #short description about this highlight (i assume) needs further info e.g. Elton John is a world-wide pop singer
#     #file = file #needs speccing
#     record_link = RecordChooserBlock() #link to relevant records, e.g. Elton John's letter to the Queen #could this be done automatically? (most likely not)
#     #date = date #need speccing
 
#     highlight_tag_names = models.TextField(editable=False)
#     tags = ClusterTaggableManager(through=TaggedHighlights, blank=True)
 
#     search_fields = Page.search_fields + [
#         index.SearchField("highlight_tag_names"),
#     ]
 
#     def save(self, *args, **kwargs):
#         """
#         Overrides Page.save() to ensure 'highlight_tag_names' always reflects the tags() value
#         """
#         if (
#             "update_fields" not in kwargs
#             or "highlight_tag_names" in kwargs["update_fields"]
#         ):
#             self.highlight_tag_names = "\n".join(t.name for t in self.tags.all())
#         super().save(*args, **kwargs)
 
 
#     def get_context(self, request):
#         context = super().get_context(request)
#         closer_look = self.get_children().specific()[0]
#         context["closer_look"] = closer_look
#         return context
   
#     content_panels = BasePage.content_panels + [
#         #FieldPanel("title"),
#         FieldPanel("short_description"),
#         #FieldPanel("file"),
#         #FieldPanel("record_link"),
#         #FieldPanel("date"),
#         FieldPanel("tags"),
#     ]
 
#     parent_page_types = ["highlights.HighlightsIndexPage"]
#     subpage_types = ["highlights.CloserLookPage"]
 
 
# class CloserLookPage(BasePage):
#     """CloserLookPage
 
#     This page is ______.
#     """
#     meta_description = models.CharField(max_length=250, blank = False, null=False) #needs more info
#     #date = date #more info
#     #record_description = record_description #more info
#     #record_link = record_link #more info
#     #image = image #i assume images of elton john but more info
#     #image_library_link = image_library_link #link to a bunch of images needs more info
#     #print_on_demand_link = print_on_demand_link #again more info
#     featured_story = models.ForeignKey(
#         "insights.InsightsPage", blank=True, null=True, on_delete=models.SET_NULL
#     ) #link to featured story (insight?) but need more info
#     #tags = tags #can pull these in from parent potentially?
#     #primary_topic = primary_topic #specific tag, for elton john could be music (or british people) could generate via tag or just let the editor select the link to that exact topic gallery?
#     #primary_time_period = primary_time_period #specific tag, for elton john could be 1960-today. could generate via tag or just let the editor select the link to that exact time period gallery?
 
#     content_panels = BasePage.content_panels + [
#         FieldPanel("meta_description"),
#         #FieldPanel("date"),
#         #FieldPanel("record_description"),
#         #FieldPanel("record_link"),
#         #FieldPanel("image"),
#         #FieldPanel("image_library_link"),
#         #FieldPanel("print_on_demand_link"),
#         FieldPanel("featured_story"),
#         #FieldPanel("tags"),
#         #FieldPanel("primary_topic"),
#         #FieldPanel("primary_time_period"),
#     ]
 
 
#     parent_page_types = ["highlights.HighlightsPage"]
#     subpage_types = []
