from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField

from etna.core.models import BasePage

from ..alerts.models import AlertMixin
from .blocks import HomePageStreamBlock


class HomePage(AlertMixin, BasePage):

    body = StreamField(HomePageStreamBlock, blank=True, null=True)

    content_panels = BasePage.content_panels + [
        StreamFieldPanel('body'),
    ]
    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels

    def get_context(self, request):
        context = super().get_context(request)

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
