from django.conf import settings

from wagtail import blocks

from .paragraph import APIRichTextBlock


class ContactBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    address = APIRichTextBlock(
        required=False, features=settings.INLINE_RICHTEXT_FEATURES
    )
    telephone = blocks.CharBlock(required=False)
    chat_link = blocks.URLBlock(required=False)
    chat_note = APIRichTextBlock(required=False)
    email = blocks.EmailBlock(required=False)
    website_link = blocks.URLBlock(required=False)
    social_media = APIRichTextBlock(
        required=False, features=settings.INLINE_RICHTEXT_FEATURES
    )
