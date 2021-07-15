from django.db import models

from wagtail.core.models import Page

from ..alerts.models import AlertMixin


class HomePage(AlertMixin, Page):

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
