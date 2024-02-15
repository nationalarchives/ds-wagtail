from typing import Any, Dict, List, Tuple, Union

from django.conf import settings
from django.db import models
from django.http import HttpRequest
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.images.api.fields import ImageRenditionField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from rest_framework import serializers
from taggit.models import ItemBase, TagBase

from etna.authors.models import AuthorPageMixin, AuthorTag
from etna.collections.models import TopicalPageMixin
from etna.core.models import (
    BasePageWithIntro,
    ContentWarningMixin,
    HeroImageMixin,
    NewLabelMixin,
    RequiredHeroImageMixin,
)
from etna.core.utils import skos_id_from_text
from etna.records.fields import RecordField

from .blocks import (
    ArticlePageStreamBlock,
    AuthorPromotedPagesBlock,
    FeaturedCollectionBlock,
)

class ArticleBodyMixin(models.Model):
    body = StreamField(ArticlePageStreamBlock, blank=True, null=True)

    content_panels = FieldPanel("body")

    api_fields = APIField("body")

    class Meta:
        abstract = True

def featured_article_mixin(blank=True):
    class FeaturedArticleMixin(models.Model):
        featured_article = models.ForeignKey(
            "wagtailcore.Page",
            null=True,
            blank=blank,
            on_delete=models.SET_NULL,
            related_name="+",
            verbose_name=_("featured article"),
        )

        def get_featured_article_chooser(cls, page_types: list[str] | str, **kwargs) -> PageChooserPanel:
            return PageChooserPanel("featured_article", page_types, **kwargs)
        
        api_fields = APIField("featured_article")
        
        class Meta:
            abstract = True
    
    return FeaturedArticleMixin