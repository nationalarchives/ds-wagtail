from django.conf import settings
from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from app.core.blocks import (
    CallToActionBlock,
    ContentImageBlock,
    QuoteBlock,
    YouTubeBlock,
)
from app.core.blocks.paragraph import APIRichTextBlock


class ExternalLinkBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="URL")
    link_text = blocks.CharBlock()

    class Meta:
        label = _("External link")
        icon = "link"


class InformationPageStreamBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(
        form_classname="title",
        label="Heading",
        icon="title",
    )
    paragraph = APIRichTextBlock(
        required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )
    image = ContentImageBlock()
    quote = QuoteBlock()
    embed = YouTubeBlock()
    call_to_action = CallToActionBlock()
