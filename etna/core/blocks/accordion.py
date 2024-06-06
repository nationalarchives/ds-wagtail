from django.conf import settings

from wagtail import blocks

from .paragraph import APIRichTextBlock


class AccordionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    body = APIRichTextBlock(
        required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )

    class Meta:
        icon = "list-ul"
        label = "Accordion"


class AccordionsBlock(blocks.StructBlock):
    accordion = blocks.ListBlock(AccordionBlock())
