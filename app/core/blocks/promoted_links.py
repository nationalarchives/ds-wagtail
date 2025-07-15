from wagtail import blocks

from app.core.blocks.image import APIImageChooserBlock
from app.core.blocks.page_chooser import APIPageChooserBlock



class PromotedLinkBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="External URL", help_text="URL for the external page")
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page")
    teaser_image = APIImageChooserBlock(
        help_text="Image that will appear on thumbnails and promos around the site."
    )
    description = blocks.CharBlock(
        max_length=200, help_text="A description of the promoted page"
    )


class FeaturedPageBlock(blocks.StructBlock):
    """
    Block for featuring a page.
    """

    page = APIPageChooserBlock(
        label="Page",
        required=True,
        page_type="wagtailcore.Page",
    )

    teaser_text = blocks.CharBlock(
        label="Teaser text override",
        required=False,
        help_text="Optional override for the teaser text",
    )

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        if value.get("page"):
            if value.get("teaser_text"):
                representation["page"]["teaser_text"] = value.get("teaser_text")
            del representation["teaser_text"]
        return representation

    class Meta:
        icon = "doc-full"
        label = "Featured page"


class FeaturedExternalLinkBlock(blocks.StructBlock):
    """
    Block for featuring a link to an external site.
    """

    title = blocks.CharBlock(
        label="Title",
        max_length=100,
    )

    description = blocks.CharBlock(
        label="Description",
    )

    url = blocks.URLBlock(
        label="URL",
    )

    image = APIImageChooserBlock(
        label="Image",
        required=False,
    )

    class Meta:
        icon = "doc-full"
        label = "Featured external link"


class FeaturedPagesBlock(blocks.StreamBlock):
    featured_page = FeaturedPageBlock()
    featured_external_link = FeaturedExternalLinkBlock()

    class Meta:
        icon = "doc-full"
        label = "Featured pages list"
