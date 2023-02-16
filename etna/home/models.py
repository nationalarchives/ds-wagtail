from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField

from etna.alerts.models import AlertMixin
from etna.articles.blocks import FeaturedCollectionBlock
from etna.core.models import BasePage

from .blocks import HomePageStreamBlock


class HomePage(AlertMixin, BasePage):
    sub_heading = RichTextField(
        verbose_name=_("introductory text"),
        help_text=_(
            "1-2 sentences introducing the subject of the page, and explaining why a user should read on."
        ),
        features=settings.INLINE_RICH_TEXT_FEATURES,
        max_length=300,
    )
    featured_article = models.ForeignKey(
        "articles.ArticlePage", blank=True, null=True, on_delete=models.SET_NULL
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
        FieldPanel("featured_article", heading=_("Featured article")),
        FieldPanel("featured_pages"),
    ]

    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels

    # DataLayerMixin overrides
    gtm_content_group = "Homepage"

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
