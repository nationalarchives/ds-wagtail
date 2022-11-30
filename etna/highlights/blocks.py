from wagtail.core import blocks

from wagtail.images.blocks import ImageChooserBlock
from etna.core.blocks import ParagraphBlock
from ..records.blocks import RecordChooserBlock


class HighlightsRecordBlock(blocks.StructBlock):
    record = RecordChooserBlock()
    date = blocks.CharBlock(
        max_length=100,
        required=True,
        help_text="Date(s) related to the record (max. character length: 100)",
    )
    paragraph = ParagraphBlock()

    class Meta:
        icon = "archive"


class PromotedItemBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="External URL", help_text="URL for the external page")
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page")
    teaser_image = ImageChooserBlock(
        help_text="An image used to create a teaser for the promoted page"
    )
    author = blocks.CharBlock(required=False)
    publication_date = blocks.DateBlock(required=False)
    description = blocks.CharBlock(
        max_length=200, help_text="A description of the promoted page (max. character length: 200)"
    )


class PromotedPagesBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100)
    promoted_items = blocks.ListBlock(PromotedItemBlock, min=1, max=3)

    class Meta:
        template = "collections/blocks/promoted_pages.html"
        help_text = "Block used promote external pages"
        icon = "th-large"