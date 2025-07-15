from wagtail import blocks

from app.core.blocks import APIPageChooserBlock, ParagraphBlock, ParagraphWithHeading
from app.core.blocks.image import APIImageChooserBlock


class FeaturedExternalPageBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="external URL", help_text="URL for the external page")
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page")
    teaser_image = APIImageChooserBlock(
        help_text="Image that will appear on thumbnails and promos around the site."
    )
    description = blocks.CharBlock(
        max_length=200, help_text="A description of the promoted page"
    )

    class Meta:
        help_text = "Block used to feature a page external to Wagtail or a Record"
        icon = "star"


class FeaturedPageBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=100,
        required=False,
        help_text="Optionally override the page's title",
    )
    page = APIPageChooserBlock(required_api_fields=["teaser_image"])
    description = blocks.CharBlock(
        max_length=200, help_text="A description of the promoted page"
    )

    class Meta:
        help_text = "Block used to feature a page from within Wagtail"
        icon = "star"


class FeaturedItemBlock(blocks.StreamBlock):
    featured_page = FeaturedPageBlock()
    featured_external_page = FeaturedExternalPageBlock()

    class Meta:
        icon = "arrow-up"


class FeaturedItemsBlock(blocks.ListBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(FeaturedItemBlock, *args, **kwargs)

    class Meta:
        help_text = "Block used to feature pages from within and external to Wagtail"
        icon = "list"


class HomePageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    paragraph_with_heading = ParagraphWithHeading()
