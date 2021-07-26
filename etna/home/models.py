from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from ..alerts.models import AlertMixin
from .blocks import HomePageStreamBlock

class HomePage(AlertMixin, Page):

    body = StreamField(HomePageStreamBlock, blank=True, null=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]
    settings_panels = Page.settings_panels + AlertMixin.settings_panels

    def get_context(self, request):
        context = super().get_context(request)

        context["etna_index_pages"] = [
            {
                "title": "Collection Explorer",
                "introduction": "A new way to discover collections at The National Archives, through records hand-picked by our experts.",
                "url": "#",
            },
            {
                "title": "Collection Insights",
                "introduction": "Learn about the people, themes and events featured in our records, told through words, pictures and audio - discover the human stories behind the collection.",
                "url": "#",
            },
            {
                "title": "Collection Details",
                "introduction": "View and navigate records from The National Archives catalogue.",
                "url": "#",
            },
        ]

        return context
