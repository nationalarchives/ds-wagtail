from django.conf import settings
from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock

from app.core.serializers import DefaultPageSerializer

from .paragraph import APIRichTextBlock


class DoDontBlock(blocks.StructBlock):
    text = APIRichTextBlock(features=settings.INLINE_RICH_TEXT_FEATURES)


class DoDontListBlock(blocks.StructBlock):
    do = blocks.ListBlock(DoDontBlock(icon="check", label="Do item"), label="Dos")
    dont = blocks.ListBlock(
        DoDontBlock(icon="cross", label="Don't item"), label="Don'ts"
    )

    class Meta:
        icon = "tasks"
        label = "Do/Don't List"


class DescriptionListItemBlock(blocks.StructBlock):
    term = blocks.CharBlock(required=True)
    detail = APIRichTextBlock(features=settings.INLINE_RICH_TEXT_FEATURES)

    class Meta:
        icon = "list-ul"
        label = "Description List Item"


class DescriptionListBlock(blocks.StructBlock):
    items = blocks.ListBlock(DescriptionListItemBlock())

    class Meta:
        icon = "list-ul"
        label = "Description List"


class PeopleListingBlock(blocks.StructBlock):
    """
    A block for listing people with their roles.
    """

    role = SnippetChooserBlock(
        "people.PersonRole",
        label="Role selection",
        help_text="Select a role to filter people by their roles.",
    )

    def get_api_representation(self, value, context=None):
        role = value.get("role")

        if not role:
            return {}

        people = role.person_roles.all()

        if not people:
            return {}

        return {
            "role": role.name,
            "people": [
                (
                    DefaultPageSerializer().to_representation(person.person)
                    if person.person
                    else None
                )
                for person in people
            ],
        }

    class Meta:
        icon = "user"
        label = "People Listing"
