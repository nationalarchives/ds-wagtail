from app.core.blocks.links import (
    InternalLinkBlock,
    LinkBlock,
    LinkColumnWithHeaderBlock,
)
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField


@register_setting(icon="list-ul")
class NavigationSettings(BaseSiteSetting):
    primary_navigation = StreamField(
        [("link", InternalLinkBlock())],
        blank=True,
        help_text="Main site navigation",
    )
    secondary_navigation = StreamField(
        [("link", InternalLinkBlock())],
        blank=True,
        help_text="Alternative navigation",
    )
    footer_navigation = StreamField(
        [("column", LinkColumnWithHeaderBlock())],
        blank=True,
        help_text="Multiple columns of footer links with optional header.",
    )
    footer_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Single list of elements at the base of the page.",
    )

    panels = [
        FieldPanel("primary_navigation"),
        FieldPanel("secondary_navigation"),
        FieldPanel("footer_navigation"),
        FieldPanel("footer_links"),
    ]
