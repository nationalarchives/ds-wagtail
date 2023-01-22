from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from wagtailmetadata.models import MetadataPageMixin

from etna.core.models import BasePage
from etna.teasers.models import TeaserImageMixin

from ..alerts.models import AlertMixin
from ..article.blocks import FeaturedCollectionBlock
from .blocks import HomePageStreamBlock


class HomePage(AlertMixin, TeaserImageMixin, MetadataPageMixin, BasePage):
    sub_heading = models.CharField(
        max_length=255,
        blank=False,
        default="Discover some of the most important and unusual records from over 1000 "
        "years of history.",
    )
    featured_article = models.ForeignKey(
        "article.ArticlePage", blank=True, null=True, on_delete=models.SET_NULL
    )
    body = StreamField(HomePageStreamBlock, blank=True, null=True, use_json_field=True)
    featured_pages = StreamField(
        [("featuredpages", FeaturedCollectionBlock())],
        blank=True,
        null=True,
        use_json_field=True,
    )
    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("body"),
        FieldPanel("featured_article", heading=_("Featured Article")),
        FieldPanel("featured_pages"),
    ]
    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels
    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels

    def get_context(self, request):
        context = super().get_context(request)
        article_pages = self.get_children().live().specific()
        context["article_pages"] = article_pages
        context["etna_index_pages"] = [
            {
                "title": "Collection Explorer",
                "introduction": (
                    "A new way to discover collections at The National Archives, "
                    "through records hand-picked by our experts."
                ),
                "url": "#",
            },
            {
                "title": "Collection Insights",
                "introduction": (
                    "Learn about the people, themes and events featured in our records, "
                    "told through words, pictures and audio - discover the human stories behind the collection."
                ),
                "url": "#",
            },
            {
                "title": "Collection Details",
                "introduction": "View and navigate records from The National Archives catalogue.",
                "url": "#",
            },
        ]

        return context
