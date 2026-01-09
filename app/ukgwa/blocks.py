from wagtail import blocks

from app.core.blocks import (
    CallToActionBlock,
    ContentImageBlock,
    ParagraphBlock,
    QuoteBlock,
    SubHeadingBlock,
    YouTubeBlock,
)


class InformationPageStreamBlock(blocks.StreamBlock):
    sub_heading = SubHeadingBlock()
    paragraph = ParagraphBlock()
    image = ContentImageBlock()
    quote = QuoteBlock()
    youtube_video = YouTubeBlock()
    call_to_action = CallToActionBlock()
