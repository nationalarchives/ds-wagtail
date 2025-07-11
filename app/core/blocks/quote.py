from django.conf import settings
from wagtail import blocks

from app.core.blocks.paragraph import APIRichTextBlock


class QuoteBlock(blocks.StructBlock):
    """
    Quote streamfield component
    """

    quote = APIRichTextBlock(
        required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )
    attribution = blocks.CharBlock(required=False, max_length=100)

    class Meta:
        icon = "openquote"
        label = "Quote"


class ReviewBlock(blocks.StructBlock):
    """
    Gives an editor the ability to add a review from an entity, e.g.
    a newspaper, that has given us a review. A quote block with stars.
    """

    quote = APIRichTextBlock(required=True, features=settings.INLINE_RICH_TEXT_FEATURES)
    attribution = blocks.CharBlock(required=True, max_length=100)
    stars = blocks.ChoiceBlock(
        choices=[
            (0, "No stars"),
            (3, "3 stars"),
            (4, "4 stars"),
            (5, "5 stars"),
        ],
        icon="pick",
        required=True,
        default=0,
    )

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        representation["stars"] = int(value.get("stars"))
        return representation

    class Meta:
        icon = "pick"
        label = "Review"
