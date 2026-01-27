from app.core.blocks.image import APIImageChooserBlock
from app.core.blocks.page_chooser import APIPageChooserBlock
from wagtail import blocks


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

    supertitle = blocks.CharBlock(
        label="Supertitle",
        max_length=20,
        required=False,
    )

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
