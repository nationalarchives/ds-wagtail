import factory
from etna.collections import models as app_models
from etna.core.factories import BasePageFactory
from wagtail_factories import ImageFactory


class ExplorerIndexPageFactory(BasePageFactory):
    articles_introduction = "These are the articles"

    class Meta:
        model = app_models.ExplorerIndexPage


class TopicIndexPageFactory(BasePageFactory):
    articles_introduction = "These are the articles"

    class Meta:
        model = app_models.TopicExplorerIndexPage


class TopicPageFactory(BasePageFactory):
    hero_image = factory.SubFactory(ImageFactory)
    hero_image_caption = "<p>Hero image caption</p>"

    class Meta:
        model = app_models.TopicExplorerPage


class TimePeriodIndexPageFactory(BasePageFactory):
    articles_introduction = "These are the articles"

    class Meta:
        model = app_models.TopicExplorerIndexPage


class TimePeriodPageFactory(BasePageFactory):
    hero_image = factory.SubFactory(ImageFactory)
    hero_image_caption = "<p>Hero image caption</p>"
    start_year = 1800

    class Meta:
        model = app_models.TimePeriodExplorerPage
