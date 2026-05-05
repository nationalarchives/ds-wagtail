from app.core.blocks.paragraph import APIRichTextBlock
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


class SourceMediaBlock(MediaBlock):
    title = None
