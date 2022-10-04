from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from wagtailmetadata.models import MetadataPageMixin

from etna.core.models import BasePage
from etna.teasers.models import TeaserImageMixin

from ..alerts.models import AlertMixin
from .blocks import HomePageStreamBlock


class HomePage(AlertMixin, TeaserImageMixin, MetadataPageMixin, BasePage):
    body = StreamField(HomePageStreamBlock, blank=True, null=True, use_json_field=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]
    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels
    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels

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
