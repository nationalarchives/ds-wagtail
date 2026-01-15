from app.core.blocks import (
    CallToActionBlock,
    ContentImageBlock,
    ParagraphBlock,
    QuoteBlock,
    SubHeadingBlock,
    SubSubHeadingBlock,
    YouTubeBlock,
)
from django.core.exceptions import ValidationError
from wagtail import blocks


class SectionContentBlock(blocks.StreamBlock):
    call_to_action = CallToActionBlock()
    image = ContentImageBlock()
    paragraph = ParagraphBlock()
    quote = QuoteBlock()
    sub_heading = SubHeadingBlock()
    sub_sub_heading = SubSubHeadingBlock()
    youtube_video = YouTubeBlock()


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"

    def clean(self, value):
        clean = super().clean(value)
        has_sub_heading = False
        content = clean.get("content")

        for block in content:
            block_type = block.block_type
            if block_type == "sub_heading":
                has_sub_heading = True
            elif block_type == "sub_sub_heading" and not has_sub_heading:
                raise ValidationError(
                    "A sub-sub-heading was found before any sub-headings."
                )
        return clean


class InformationPageStreamBlock(SectionContentBlock):
    content_section = ContentSectionBlock()
    sub_heading = None
    sub_sub_heading = None
