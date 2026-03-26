from app.core.blocks import (
    CallToActionBlock,
    ContentImageBlock,
    ParagraphBlock,
    QuoteBlock,
    SubHeadingBlock,
    SubSubHeadingBlock,
    YouTubeBlock,
)
from app.core.blocks.links import LinkBlock
from django.core.exceptions import ValidationError
from wagtail import blocks


class LinkWithDescriptionBlock(LinkBlock):
    """
    Extends LinkBlock with a required description field.
    """

    description = blocks.CharBlock(
        label="Description",
        required=True,
        help_text="Required description shown beneath the link",
    )

    def get_api_representation(self, value, context=None):
        rep = super().get_api_representation(value, context)
        rep["description"] = value.get("description", "")
        return rep

    class Meta:
        label = "Link"
        icon = "link"


class BookmarkletBlock(blocks.StructBlock):
    def get_api_representation(self, value, context=None):
        return True

    class Meta:
        icon = "link"
        label = "Bookmarklet"
        help_text = "Adds a draggable bookmarklet button to the page."


class SectionContentBlock(blocks.StreamBlock):
    call_to_action = CallToActionBlock()
    image = ContentImageBlock()
    paragraph = ParagraphBlock()
    quote = QuoteBlock()
    sub_heading = SubHeadingBlock()
    sub_sub_heading = SubSubHeadingBlock()
    youtube_video = YouTubeBlock()
    bookmarklet = BookmarkletBlock()

    class Meta:
        block_counts = {
            "bookmarklet": {"max_num": 1},
        }


class ContentSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"

    def clean(self, value):
        clean = super().clean(value)
        content = clean.get("content")

        for block in content:
            block_type = block.block_type
            if block_type == "sub_heading":
                break  # Found a sub-heading first; any subsequent headings are valid.
            elif block_type == "sub_sub_heading":
                raise ValidationError(
                    "A sub-sub-heading was found before any sub-headings."
                )
        return clean


class InformationPageStreamBlock(SectionContentBlock):
    content_section = ContentSectionBlock()
    sub_heading = None
    sub_sub_heading = None

    def clean(self, value, **kwargs):
        clean = super().clean(value, **kwargs)
        nested = [
            block
            for section in clean
            if section.block_type == "content_section"
            for block in section.value["content"]
        ]
        if sum(block.block_type == "bookmarklet" for block in [*clean, *nested]) > 1:
            raise ValidationError("Only one bookmarklet block is allowed per page.")
        return clean
