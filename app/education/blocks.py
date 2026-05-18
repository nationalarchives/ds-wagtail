from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from app.core.blocks import (
    APIImageChooserBlock,
    APIRichTextBlock,
    FeaturedExternalLinkBlock,
    FeaturedPageBlock,
    InsetTextBlock,
    ParagraphBlock,
    PartnerLogoChooserBlock,
    QuoteBlock,
    YouTubeBlock,
)
from app.media.blocks import MediaBlock

# Resources - Source


class SourceImageWithCaptionBlock(blocks.StructBlock):
    image = APIImageChooserBlock(
        rendition_size="max-900x900",
        help_text="An image for the source.",
    )
    caption = APIRichTextBlock(features=["bold", "italic"], required=False)


class SourceMediaWithCaptionBlock(MediaBlock):
    title = None
    caption = APIRichTextBlock(features=["bold", "italic"], required=False)


class SourceYouTubeWithCaptionBlock(MediaBlock):
    youtube = YouTubeBlock()
    caption = APIRichTextBlock(features=["bold", "italic"], required=False)


class SourceMediaBlock(blocks.StreamBlock):
    image = SourceImageWithCaptionBlock()
    video = SourceMediaWithCaptionBlock()
    youtube = SourceYouTubeWithCaptionBlock()

    class Meta:
        label = "Source media"


class SourceFeaturedLinkBlock(blocks.StreamBlock):
    external_link = FeaturedExternalLinkBlock()
    internal_link = FeaturedPageBlock()

    class Meta:
        label = "Source featured link"


class SourceQuestionBlock(blocks.StreamBlock):
    question = blocks.StructBlock(
        [
            (
                "question_heading",
                blocks.CharBlock(
                    required=False,
                    max_length=255,
                ),
            ),
            (
                "question_description",
                APIRichTextBlock(
                    features=["bold", "italic", "link", "ul"],
                    required=False,
                ),
            ),
        ],
        icon="help",
    )

class SectionContentBlock(blocks.StreamBlock):
    description = ParagraphBlock()
    partner_logo = PartnerLogoChooserBlock()
    quote = QuoteBlock()
    inset_text = InsetTextBlock()


class SessionDescriptionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        group = "Basic text"

