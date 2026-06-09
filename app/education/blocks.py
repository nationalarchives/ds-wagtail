from django.conf import settings
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
from app.core.blocks.section import SubHeadingBlock
from app.media.blocks import MediaBlock

# Resources - Source


class SourceImageWithCaptionBlock(blocks.StructBlock):
    image = APIImageChooserBlock(
        rendition_size="max-900x900",
        help_text="An image for the source.",
    )
    caption = APIRichTextBlock(features=["bold", "italic"], required=False)

    class Meta:
        group = "Video, audio and downloads"


class SourceMediaBlock(blocks.StreamBlock):
    image = SourceImageWithCaptionBlock()
    media = MediaBlock()
    youtube = YouTubeBlock()

    class Meta:
        label = "Source media"


class SourceFeaturedLinkBlock(blocks.StreamBlock):
    external_link = FeaturedExternalLinkBlock()
    internal_link = FeaturedPageBlock()

    class Meta:
        label = "Source featured link"


class SourceQuestionItemBlock(blocks.StructBlock):
    question_heading = blocks.CharBlock(
        required=False,
        max_length=255,
    )
    question_description = APIRichTextBlock(
        features=settings.EXPANDED_RICH_TEXT_FEATURES,
        required=False,
    )

    class Meta:
        icon = "help"
        label = "Question"


class SourceQuestionBlock(blocks.StreamBlock):
    question = SourceQuestionItemBlock()

    class Meta:
        label = "Source question"


class TeachersNotesBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    sub_heading = SubHeadingBlock()
    inset_text = InsetTextBlock()


class TeachingResourceExtensionActivitiesBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    sub_heading = SubHeadingBlock()
    featured_page = FeaturedPageBlock()
    featured_external_link = FeaturedExternalLinkBlock()


class TeachingResourceBackgroundInformationBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    sub_heading = SubHeadingBlock()


class TeachingResourceFurtherInformationBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    sub_heading = SubHeadingBlock()
    featured_external_link = FeaturedExternalLinkBlock()
    featured_page = FeaturedPageBlock()


class SectionContentBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    partner_logo = PartnerLogoChooserBlock()
    quote = QuoteBlock()
    inset_text = InsetTextBlock()


class SessionDescriptionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        group = "Basic text"
