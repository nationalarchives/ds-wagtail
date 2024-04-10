from django.conf import settings
from django.utils.html import format_html

from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock

from etna.core.blocks import (
    ContentImageBlock,
    NoCaptionImageBlock,
    PageListBlock,
    ParagraphBlock,
    QuoteBlock,
    SectionDepthAwareStructBlock,
)
from etna.core.blocks.image import APIImageChooserBlock
from etna.core.blocks.paragraph import APIRichTextBlock

from ..records.blocks import RecordLinksBlock


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

    category = SnippetChooserBlock("categories.Category")
    summary = APIRichTextBlock(
        required=False, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    promoted_items = blocks.ListBlock(PromotedListItemBlock())

    class Meta:
        icon = "external-link-alt"
        label = "Link list"
        template = "articles/blocks/promoted_list_block.html"


class RelatedItemBlock(SectionDepthAwareStructBlock):
    title = blocks.CharBlock(
        max_length=100,
        help_text="Title of the promoted page",
    )
    description = blocks.TextBlock(
        help_text="A description of the promoted page",
    )
    teaser_image = APIImageChooserBlock(
        help_text="Image that will appear on thumbnails and promos around the site."
    )
    url = blocks.URLBlock(label="external URL", help_text="URL for the external page")

    class Meta:
        icon = "external-link-alt"
        help_text = "Block used promote an external page"
        template = "articles/blocks/related_item.html"


class FeaturedCollectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100)
    description = blocks.TextBlock(max_length=200)
    items = PageListBlock(
        "articles.ArticlePage",
        exclude_drafts=True,
        exclude_private=True,
        select_related=["teaser_image"],
        min_num=3,
        max_num=9,
    )

    class Meta:
        icon = "list"
        label = "Featured pages"
        template = "articles/blocks/featured_collection.html"


class SubHeadingBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Sub-heading")

    class Meta:
        icon = "heading"
        label = "Sub-heading"
        template = "articles/blocks/sub_heading.html"


class SectionContentBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    quote = QuoteBlock()
    sub_heading = SubHeadingBlock()
    image = ContentImageBlock()
    # media = MediaBlock()
    promoted_item = PromotedItemBlock()
    promoted_list = PromotedListBlock()
    record_links = RecordLinksBlock()


class ContentSectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        template = "articles/blocks/section.html"


class ArticlePageStreamBlock(blocks.StreamBlock):
    content_section = ContentSectionBlock()
