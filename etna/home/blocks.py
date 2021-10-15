from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..paragraphs.blocks import ParagraphWithHeading
from ..media.blocks import ImageBlock

class FeaturedExternalPageBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="external URL", help_text="URL for the external page")
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page")
    teaser_image = ImageChooserBlock(
        help_text="An image used to create a teaser for the promoted page"
    )
    description = blocks.CharBlock(
        max_length=200, help_text="A description of the promoted page"
    )

    class Meta:
        template = "home/blocks/featured_external_page.html"
        help_text = "Block used to feature a page external to Wagtail or a RecordPage"
        icon = "fa-star-o"


class FeaturedPageBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=100, required=False, help_text="Optionally override the page's title"
    )
    page = blocks.PageChooserBlock()
    description = blocks.CharBlock(
        max_length=200, help_text="A description of the promoted page"
    )

    class Meta:
        template = "home/blocks/featured_page.html"
        help_text = "Block used to feature a page from within Wagtail"
        icon = "fa-star-o"


class FeaturedItemBlock(blocks.StreamBlock):
    featured_page = FeaturedPageBlock()
    featured_external_page = FeaturedExternalPageBlock()

    class Meta:
        icon = "fa-arrow-up"


class FeaturedItemsBlock(blocks.ListBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(FeaturedItemBlock, *args, **kwargs)

    class Meta:
        template = "home/blocks/featured_items.html"
        help_text = "Block used to feature pages from within and external to Wagtail"
        icon = "fa-list"


class HomePageStreamBlock(blocks.StreamBlock):
    featured_items = FeaturedItemsBlock()
    paragraph_with_heading = ParagraphWithHeading()
    image_block = ImageBlock()
