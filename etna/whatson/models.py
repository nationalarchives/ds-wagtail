from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey

from wagtail.admin.panels import (
    FieldPanel,
    PageChooserPanel,
    InlinePanel,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from wagtail.models import Orderable

from etna.core.models import BasePageWithIntro
from etna.collections.models import TopicalPageMixin
from .blocks import EventPageBlock
from etna.articles.models import ArticleTagMixin

@register_snippet
class EventType(models.Model):
    """
    This snippet model is used so that editors can add event types,
    which we use via the event_type ForeignKey to add event types 
    to event pages.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        help_text=_("The name of the event type."),
    )

    class Meta:
        verbose_name = _("Event type")
        verbose_name_plural = _("Event types")

    def __str__(self):
        return self.name
    
@register_snippet
class AudienceType(models.Model):
    """
    This snippet model is used so that editors can add audience types,
    which we use via the audience_type ForeignKey to add audience types 
    to event pages.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        help_text=_("The name of the audience type."),
    )

    class Meta:
        verbose_name = _("Audience type")
        verbose_name_plural = _("Audience types")

    def __str__(self):
        return self.name
    
class AudienceTypeOrderable(Orderable):
    """
    This model is used to add multiple audience types to event pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="event_audience_types",
    )

    access_type = models.ForeignKey(
        "whatson.AudienceType",
        on_delete=models.CASCADE,
        related_name="audience_types",
    )
    
@register_snippet
class AccessType(models.Model):
    """
    This snippet model is used so that editors can add access types,
    which we use via the AccessTypeOrderable to add multiple access 
    types to event pages.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        help_text=_("The type of access descriptor"),
    )

    class Meta:
        verbose_name = _("Access type")
        verbose_name_plural = _("Access types")

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name
    
class AccessTypeOrderable(Orderable):
    """
    This model is used to add multiple access types to event pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="event_access_types",
    )

    access_type = models.ForeignKey(
        "whatson.AccessType",
        on_delete=models.CASCADE,
        related_name="access_types",
    )

class WhatsOnPage(BasePageWithIntro):
    """WhatsOnPage
    
    A page for listing events.
    """

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("What's On page")

    parent_page_types = ["home.HomePage",]
    subpage_types = ["whatson.EventPage",]

    content_panels = BasePageWithIntro.content_panels


class EventPage(ArticleTagMixin, TopicalPageMixin, BasePageWithIntro):
    """EventPage

    A page for an event.
    """
        
    lead_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # body = StreamField(
    #     EventPageBlock,
    #     blank=True,
    #     null=True,
    #     help_text="Add content for this page",
    #     use_json_field=True
    # )

    event_type = models.ForeignKey(
        EventType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    short_title = models.CharField(
        max_length=75,
        verbose_name=_("short title"),
        help_text=_(
            "A short title for the event. This will be used in the event listings."
        ),
        blank=True,
        null=True,
    )

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("Event page")

    content_panels = BasePageWithIntro.content_panels + [
        FieldPanel("lead_image"),
        # FieldPanel("body"),
        FieldPanel("event_type"),
        InlinePanel("event_access_types",
                    heading=_("Access types"),
            help_text=_(
                "If the event has more than one access type, please add these in order of relevance from most to least."
            )),
        InlinePanel("event_audience_types",
                    heading=_("Audience types"),
            help_text=_(
                "If the event has more than one audience type, please add these in order of relevance from most to least."
            )),
    ]

    promote_panels = (
        BasePageWithIntro.promote_panels
        + [
            FieldPanel("short_title"),
        ]
        + ArticleTagMixin.promote_panels
        + [
            TopicalPageMixin.get_topics_inlinepanel(),
            TopicalPageMixin.get_time_periods_inlinepanel(),
        ]
    )

    search_fields = (
        BasePageWithIntro.search_fields
        + ArticleTagMixin.search_fields
        + [
            index.SearchField("topic_names", boost=1),
            index.SearchField("time_period_names", boost=1),
        ]
    )

    parent_page_types = ["whatson.WhatsOnPage",]
    subpage_types = []
