from django.conf import settings
from wagtail import blocks

from .paragraph import APIRichTextBlock


class ContactBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    body = APIRichTextBlock(required=False, features=["link"])
    address = blocks.TextBlock(
        required=False, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    telephone = blocks.CharBlock(required=False)
    chat_link = blocks.URLBlock(required=False)
    chat_note = APIRichTextBlock(required=False)
    email = blocks.EmailBlock(required=False)
    website_link = blocks.URLBlock(required=False)
    social_media = APIRichTextBlock(
        required=False, features=settings.INLINE_RICH_TEXT_FEATURES
    )

    class Meta:
        icon = "mail"
        label = "Contact"
