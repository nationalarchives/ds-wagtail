from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    PageChooserPanel,
    MultiFieldPanel,
)
from wagtail.api import APIField
from wagtail.fields import StreamField
from etna.components.core.models import FeaturedPage

from .blocks import (
    ArticlePageStreamBlock,
)

# class ArticleBodyMixin(models.Model):
#     body = StreamField(ArticlePageStreamBlock, blank=True, null=True)

#     content_panels = FieldPanel("body")

#     api_fields = APIField("body")

#     class Meta:
#         abstract = True

class ArticleBody():
    body = StreamField(ArticlePageStreamBlock, blank=True, null=True)

    content_panels = FieldPanel("body")

    api_fields = APIField("body")

    class Meta:
        abstract = True


class ArticleBody:
    def get_chooser(**kwargs) -> FieldPanel:
        return FieldPanel(**kwargs)

    def get_field(null: bool = True, blank: bool = True, verbose_name: str = "Body") -> StreamField:
        return StreamField(ArticlePageStreamBlock, blank=blank, null=null, verbose_name=verbose_name)

    def get_api_field(name: str = "featured_page", serializer = None) -> APIField:
        return APIField(name=name, serializer=serializer)

class GenericMixin(models.Model):
    body = StreamField(ArticlePageStreamBlock, blank=True, null=True)

    super_page = FeaturedPage.get_field(null=True, blank=True)

    content_panels = [MultiFieldPanel([FeaturedPage.get_chooser(field_name="super_page",page_type=["articles.ArticlePage"]), FieldPanel("body")], heading="Title and page content",
                classname="collapsible",), ]

    class Meta:
        abstract = True
    