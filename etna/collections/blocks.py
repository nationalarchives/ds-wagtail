from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


class CollectionHighlightsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="Collection Highlights")

    class Meta:
        template = "collections/blocks/collection_highlights.html"
        help_text = "Block used to output the list of collection highlights"
        icon = "fa-th"


class FeaturedPageBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100)
    page = blocks.PageChooserBlock()

    class Meta:
        template = "collections/blocks/featured_page.html"
        help_text = "Block used feature a page from within Wagtail"
        icon = "fa-arrow-up"


class PromotedItemBlock(blocks.StructBlock):
    url = blocks.URLBlock(
        label="external URL", help_text="URL for the external page"
    )
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page")
    teaser_image = ImageChooserBlock(
        help_text="An image used to create a teaser for the promoted page"
    )
    description = blocks.CharBlock(
        max_length=200, help_text="A description of the promoted page"
    )


class PromotedPagesBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100)
    sub_heading = blocks.CharBlock(max_length=200)
    promoted_items = blocks.ListBlock(PromotedItemBlock, min=3, max=3)

    class Meta:
        template = "collections/blocks/promoted_pages.html"
        help_text = "Block used promote external pages"
        icon = "fa-th-large"


class TopicExplorerPageStreamBlock(blocks.StreamBlock):
    collection_highlights = CollectionHighlightsBlock()
    featured_page = FeaturedPageBlock()
    promoted_pages = PromotedPagesBlock()

    class Meta:
        block_counts = {
            "collection_highlights": {"min_num": 1, "max_num": 1},
            "featured_page": {"max_num": 1},
            "promoted_pages": {"max_num": 1},
        }
