from django.conf import settings

from wagtail import blocks

from etna.core.blocks.paragraph import APIRichTextBlock


class TabBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=50)
    content = APIRichTextBlock(
        required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )

    class Meta:
        icon = "indent"
        label = "Tab"


class TabsBlock(blocks.StructBlock):
    tabs = blocks.ListBlock(TabBlock())

    class Meta:
        icon = "table-list"
        label = "Tab list"
        template = "blocks/quote.html"
