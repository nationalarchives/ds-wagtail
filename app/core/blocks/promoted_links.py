from django.conf import settings
from django.utils.html import format_html
from wagtail import blocks

from app.core.blocks.image import APIImageChooserBlock
from app.core.blocks.page_chooser import APIPageChooserBlock
from app.core.blocks.paragraph import APIRichTextBlock

from .base import SectionDepthAwareStructBlock
from .image import NoCaptionImageBlock


class PromotedLinkBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="External URL", help_text="URL for the external page")
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page")
    teaser_image = APIImageChooserBlock(
        help_text="Image that will appear on thumbnails and promos around the site."
    )
    description = blocks.CharBlock(
        max_length=200, help_text="A description of the promoted page"
    )


class AuthorPromotedLinkBlock(PromotedLinkBlock):
    publication_date = blocks.CharBlock(
        required=False,
        help_text="This is a free text field. Please enter date as per agreed format: 14 April 2021",
    )
    author = blocks.CharBlock(required=False)


class AuthorPromotedPagesBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100)
    promoted_items = blocks.ListBlock(AuthorPromotedLinkBlock, max_num=3)

    class Meta:
        template = "articles/blocks/promoted_pages.html"
        help_text = "Block used to promote external pages"
        icon = "th-large"


class PromotedItemBlock(SectionDepthAwareStructBlock):
    title = blocks.CharBlock(
        max_length=100,
        help_text="Title of the promoted page",
        label="Title",
    )
    category = blocks.ChoiceBlock(
        label="Category",
        choices=[
            ("blog", "Blog post"),
            ("podcast", "Podcast"),
            ("video", "Video"),
            ("video-external", "External video"),
            ("external-link", "External link"),
        ],
    )
    publication_date = blocks.CharBlock(
        required=False,
        help_text="This is a free text field. Please enter date as per agreed format: 14 April 2021",
    )
    author = blocks.CharBlock(required=False)
    duration = blocks.CharBlock(
        required=False,
        max_length=50,
        label="Duration",
        help_text="Podcast or video duration.",
    )
    url = blocks.URLBlock(label="External URL", help_text="URL for the external page")
    target_blank = blocks.BooleanBlock(
        label=format_html(
            "%s <p style='font-size: 11px;'>%s</p>"
            % ("Should this URL open in a new tab?", "Tick the box if 'yes'")
        ),
        required=False,
    )
    cta_label = blocks.CharBlock(
        label="Call to action label",
        max_length=50,
        help_text=format_html(
            "%s <strong>%s</strong>'."
            % (
                "The text displayed on the button for your URL. If your URL links to an external site, "
                + "please add the name of the site users will land on, and what they will find on this page. "
                + "For example 'Watch our short film ",
                "about Shakespeare on YouTube",
            )
        ),
    )
    image = NoCaptionImageBlock(
        label="Teaser image",
        template="articles/blocks/images/blog-embed__image-container.html",
    )
    description = APIRichTextBlock(
        features=settings.INLINE_RICH_TEXT_FEATURES,
        help_text="A description of the promoted page",
    )

    class Meta:
        label = "Featured link"
        template = "articles/blocks/featured_link.html"
        help_text = "Block used promote an external page"
        icon = "star"
        form_template = "form_templates/default-form-with-safe-label.html"


class PromotedListItemBlock(SectionDepthAwareStructBlock):
    """
    Items for promoted list block.
    """

    title = blocks.CharBlock(
        required=True,
        max_length=100,
        help_text="The title of the target page",
    )
    description = APIRichTextBlock(
        required=False,
        features=settings.INLINE_RICH_TEXT_FEATURES,
        help_text="A description of the target page",
    )
    url = blocks.URLBlock(required=True)

    class Meta:
        icon = "star"


class PromotedListBlock(blocks.StructBlock):
    """
    Streamfield for collating a series of links for research or interesting pages.
    """

    summary = APIRichTextBlock(
        required=False, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    promoted_items = blocks.ListBlock(PromotedListItemBlock())

    class Meta:
        icon = "link"
        label = "Link list"
        template = "articles/blocks/promoted_list_block.html"


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
