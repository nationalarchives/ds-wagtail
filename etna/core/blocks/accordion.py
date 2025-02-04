from django.conf import settings
from wagtail import blocks

from .document import DocumentsBlock
from .paragraph import APIRichTextBlock
from .tables import TableBlock


class AccordionContentBlock(blocks.StreamBlock):
    text = APIRichTextBlock(
        required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )
    table = TableBlock()
    documents = DocumentsBlock()

    class Meta:
        icon = "list-ul"
        label = "Body"


class AccordionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    body = AccordionContentBlock()

    class Meta:
        icon = "list-ul"
        label = "Accordion Item"


class SimplifiedAccordionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    body = APIRichTextBlock(
        required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )

    class Meta:
        icon = "list-ul"
        label = "Accordion Item"


class AccordionsBlock(blocks.StructBlock):
    items = blocks.ListBlock(AccordionBlock())


class DetailsBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    body = APIRichTextBlock(
        required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )

    class Meta:
        icon = "terminal"
        label = "Details"
