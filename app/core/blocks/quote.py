from app.core.blocks.paragraph import APIRichTextBlock
from django.conf import settings
from django.core.exceptions import ValidationError
from wagtail import blocks

from .page_chooser import APIPageChooserBlock


class CitationLink(blocks.StructBlock):

    citation_internal_link = APIPageChooserBlock(
        label="Internal page",
        required=False,
        help_text="Reference another page published on the site",
    )
    citation_external_link = blocks.URLBlock(
        label="External link",
        required=False,
        help_text="Add a URL here to refer to an external source",
    )

    class Meta:
        icon = "link"
        collapsed = True


class AttributionCitationBlock(blocks.StructBlock):

    attribution = blocks.CharBlock(
        required=False,
        max_length=100,
        help_text="The name of the person being quoted. e.g. King Edward VIII",
    )

    citation = blocks.CharBlock(
        required=False,
        max_length=100,
        help_text="The title of the work or document from which the quote is taken. e.g. Instrument of Abdication, 10 December 1936. Catalogue reference: PC 11/1",
    )

    source_link = CitationLink()

    class Meta:
        icon = "edit"
        collapsed = True
        label_format = "{attribution+", " if attribution} {citation}"


class QuoteBlock(blocks.StructBlock):
    """
    Quote streamfield component
    """

    quote = APIRichTextBlock(
        required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )

    source = AttributionCitationBlock()

    def clean(self, value):
        data = super().clean(value)
        source = data.get("source") or {}
        source_link = source.get("source_link") or {}

        if source_link.get("citation_internal_link") and source_link.get(
            "citation_external_link"
        ):
            raise ValidationError(
                "You must provide either a page link or an external link, not both."
            )

        return data

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        source = representation.pop("source", {}) or {}

        citation_link = source.get("source_link") or {}
        internal_link = citation_link.get("citation_internal_link")

        return {
            "quote": representation.get("quote"),
            "attribution": source.get("attribution"),
            "citation": source.get("citation"),
            "citation_url": citation_link.get("citation_external_link")
            or (internal_link.get("full_url") if internal_link else None),
        }

    class Meta:
        icon = "openquote"
        label = "Quote"
        source = AttributionCitationBlock()


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
