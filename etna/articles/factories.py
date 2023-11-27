import factory

from wagtail_factories import ImageFactory

from etna.articles import models as app_models
from etna.core.factories import BasePageFactory


class ArticlePageFactory(BasePageFactory):
    hero_image = factory.SubFactory(ImageFactory)
    hero_image_caption = "<p>Hero image caption</p>"

    class Meta:
        model = app_models.ArticlePage
