from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    PageChooserPanel,
    MultiFieldPanel,
)
from wagtail.api import APIField
from wagtail.fields import StreamField

from .blocks import (
    ArticlePageStreamBlock,
)

# class ArticleBodyMixin(models.Model):
#     body = StreamField(ArticlePageStreamBlock, blank=True, null=True)

#     content_panels = FieldPanel("body")

#     api_fields = APIField("body")

#     class Meta:
#         abstract = True

class FeaturedArticle:
    def get_chooser(**kwargs) -> PageChooserPanel:
        return PageChooserPanel(**kwargs)

    def get_field(null=True, blank=True, verbose_name=_("featured article")) -> models.ForeignKey:
        return models.ForeignKey(
            "wagtailcore.Page",
            null=null,
            blank=blank,
            on_delete=models.SET_NULL,
            related_name="+",
            verbose_name=verbose_name,
            use_json_field=True,
        )
    
    api_fields = APIField("featured_article")



class GenericMixin(models.Model):
    body = StreamField(ArticlePageStreamBlock, blank=True, null=True)

    super_page = FeaturedArticle.get_field(null=True, blank=True)

    content_panels = [MultiFieldPanel([FeaturedArticle.get_chooser(field_name="super_page",page_type=["articles.ArticlePage"]), FieldPanel("body")], heading="Title and page content",
                classname="collapsible",), ]

    class Meta:
        abstract = True
    