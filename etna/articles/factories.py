import factory
from wagtail_factories import ImageFactory

from etna.articles import models as app_models
from etna.core.factories import BasePageFactory


class ArticleIndexPageFactory(BasePageFactory):
    class Meta:
        model = app_models.ArticleIndexPage


class ArticlePageFactory(BasePageFactory):
    hero_image = factory.SubFactory(ImageFactory)
    hero_image_caption = "<p>Hero image caption</p>"

    class Meta:
        model = app_models.ArticlePage


class RecordArticlePageFactory(BasePageFactory):
    intro_image = factory.SubFactory(ImageFactory)
    record = "C4761957"
    date_text = "Date text"
    about = "<p>About this record</p>"
    gallery_heading = "Gallery heading"

    class Meta:
        model = app_models.RecordArticlePage


class FocusedArticlePageFactory(BasePageFactory):
    hero_image = factory.SubFactory(ImageFactory)
    hero_image_caption = "<p>Hero image caption</p>"

    class Meta:
        model = app_models.FocusedArticlePage
