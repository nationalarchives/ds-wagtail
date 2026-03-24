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
    attribution = blocks.CharBlock(required=False, max_length=100, help_text="e.g. Author")

    citation = blocks.CharBlock(required=False, max_length=100, help_text="e.g. Some Book")

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
        elif not (
            data.get("citation_internal_link") or data.get("citation_external_link")
        ):
            raise ValidationError(
                "You must provide either a page link or an external link."
            )

        return data

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        internal_page = value.get("citation_internal_link")
        external_url = value.get("citation_external_link")
        citation_href = external_url or (
            internal_page.full_url if internal_page else None
        )
        citation_text_internal = None
        citation = value.get("citation")

        if citation_href:
            representation["citation_url"] = citation_href

        if internal_page:
            internal_page_specific = internal_page.specific
            citation_text_internal = (
                getattr(internal_page_specific, "short_title", None)
                or getattr(internal_page_specific, "title", None)
                or getattr(internal_page, "title", None)
            )
            if citation_text_internal:
                representation["citation_internal"] = citation_text_internal

        if citation:
            representation["citation"] = citation

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
