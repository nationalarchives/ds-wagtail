from django.conf import settings

from wagtail import blocks

from .paragraph import APIRichTextBlock


class InsetTextBlock(blocks.StructBlock):
    text = APIRichTextBlock(features=settings.RESTRICTED_RICH_TEXT_FEATURES)

    class Meta:
        icon = "indent"
        label = "Inset text"
