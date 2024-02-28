from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField

from etna.alerts.models import AlertMixin
from etna.core.models import BasePageWithIntro

from .blocks import HomePageStreamBlock


class HomePage(AlertMixin, BasePageWithIntro):
    body = StreamField(HomePageStreamBlock, blank=True, null=True)

    content_panels = BasePageWithIntro.content_panels + [
        FieldPanel("body"),
    ]

    settings_panels = BasePageWithIntro.settings_panels + AlertMixin.settings_panels

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

    api_fields = [
        APIField("intro"),
        APIField("body"),
    ]
