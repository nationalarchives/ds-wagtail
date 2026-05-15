from app.core.blocks.image import APIImageChooserBlock
from app.core.blocks.paragraph import APIRichTextBlock
from app.core.blocks.promoted_links import FeaturedExternalLinkBlock, FeaturedPageBlock
from app.core.blocks.video import YouTubeBlock
from app.media.blocks import MediaBlock
from wagtail import blocks


class QuestionBlock(blocks.StreamBlock):
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
                "guidance_for_teachers",
                APIRichTextBlock(
                    features=["bold", "italic", "link", "ul"],
                    required=False,
                ),
            ),
        ],
        icon="help",
    )


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
