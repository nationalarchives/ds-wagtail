from django.conf import settings
from wagtail import blocks
from wagtail.blocks import BlockGroup
from wagtail.snippets.blocks import SnippetChooserBlock

from app.core.serializers import DefaultPageSerializer

from .paragraph import APIRichTextBlock


class DoDontBlock(blocks.StructBlock):
    text = APIRichTextBlock(features=settings.INLINE_RICH_TEXT_FEATURES)


class DoDontListBlock(blocks.StructBlock):
    do_heading = blocks.CharBlock(
        max_length=100,
        required=False,
        label='Custom do heading (defaults to "Do")',
    )
    do = blocks.ListBlock(DoDontBlock(icon="check", label="Do item"), label="Dos")
    dont_heading = blocks.CharBlock(
        max_length=100,
        required=False,
        label="Custom don't heading (defaults to \"Don't\")",
    )
    dont = blocks.ListBlock(
        DoDontBlock(icon="cross", label="Don't item"), label="Don'ts"
    )

    class Meta:
        icon = "tasks"
        label = "Do/Don't List"
        group = "Emphasis"


class DescriptionListSettingsBlock(blocks.StructBlock):
    STYLE_CHOICES = [
        ("none", "None"),
        ("lined", "Lined"),
        ("zebra", "Zebra"),
    ]

    COLUMN_BALANCING_CHOICES = [
        ("none", "None"),
        ("even", "Even"),
        ("left-weighted", "Left-weighted"),
        ("right-weighted", "Right-weighted"),
    ]

    style = blocks.ChoiceBlock(
        choices=STYLE_CHOICES,
        default="none",
        label="Style",
        help_text="Choose the style for this description list.",
    )

    column_balancing = blocks.ChoiceBlock(
        choices=COLUMN_BALANCING_CHOICES,
        default="none",
        label="Column balancing",
        help_text="Choose the balancing for the columns of the description list.",
    )

    stacked = blocks.BooleanBlock(
        required=False,
        default=False,
        label="Stacked layout",
        help_text="If enabled, the term and detail will be stacked vertically instead of displayed side by side.",
    )

    class Meta:
        label = "Style Options"
        label_format = ""


class DescriptionListItemBlock(blocks.StructBlock):
    term = blocks.CharBlock(required=True)
    detail = APIRichTextBlock(features=settings.INLINE_RICH_TEXT_FEATURES)

    class Meta:
        icon = "list-ul"
        label = "Description List Item"
        group = "Structured and collapsible content"


class DescriptionListBlock(blocks.StructBlock):
    items = blocks.ListBlock(DescriptionListItemBlock())
    settings = DescriptionListSettingsBlock()

    class Meta:
        icon = "list-ul"
        label = "Description List"
        group = "Structured and collapsible content"
        form_layout = BlockGroup(children=["items"], settings=["settings"])


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

        people = role.person_roles.all().order_by(
            "-weighting", "person__last_name", "person__first_name"
        )

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
        group = "Onward journeys"
