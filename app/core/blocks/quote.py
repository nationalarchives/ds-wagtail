from app.core.blocks.paragraph import APIRichTextBlock
from django.conf import settings
from django.core.exceptions import ValidationError
from wagtail import blocks

from .page_chooser import APIPageChooserBlock


class QuoteBlock(blocks.StructBlock):
    """
    Quote streamfield component
    """

    quote = APIRichTextBlock(
        required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )
    attribution = blocks.CharBlock(
        required=False, max_length=100, help_text="e.g. Author"
    )

    citation = blocks.CharBlock(
        required=False, max_length=100, help_text="e.g. Some Book"
    )

    citation_internal_link = APIPageChooserBlock(
        required=False,
        help_text="Reference another page published on the site",
    )
    citation_external_link = blocks.URLBlock(
        required=False,
        help_text="Add a URL here to refer to an external source",
    )

    def clean(self, value):
        data = super().clean(value)

        if data.get("citation_internal_link") and data.get("citation_external_link"):
            raise ValidationError(
                "You must provide either a page link or an external link, not both."
            )

        return data

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        internal_link = representation.get("citation_internal_link")
        representation["citation_url"] = representation.get("citation_external_link") or (
            internal_link.get("full_url")
            if internal_link
            else None
        )
        del representation["citation_internal_link"]
        del representation["citation_external_link"]
        return representation

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
