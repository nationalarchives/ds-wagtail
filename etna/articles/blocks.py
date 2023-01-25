from django.conf import settings
from django.utils.html import format_html

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from etna.core.blocks import (
    ContentImageBlock,
    ImageBlock,
    NoCaptionImageBlock,
    PageListBlock,
    ParagraphBlock,
    SectionDepthAwareStructBlock,
)

from ..media.blocks import MediaBlock
from ..records.blocks import RecordChooserBlock


class FeaturedRecordBlock(SectionDepthAwareStructBlock):
    title = blocks.CharBlock(
        label="Descriptive title",
        max_length=200,
        help_text="A short description (max 200 characters) to add 'relevancy' to the record details. For example: 'Entry for Alice Hawkins in the index to suffragettes arrested'.",
    )
    record = RecordChooserBlock()
    image = ImageBlock(
        label="Teaser image",
        required=False,
        help_text="Add an image to be displayed with the selected record.",
        template="articles/blocks/images/blog-embed__image-container.html",
    )

    class Meta:
        icon = "archive"
        template = "articles/blocks/featured_record.html"
        label = "Featured record"


class FeaturedRecordsItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        label="Descriptive title",
        max_length=200,
        help_text="A short description (max 200 characters) to add 'relevancy' to the record details. For example: 'Entry for Alice Hawkins in the index to suffragettes arrested'.",
    )
    record = RecordChooserBlock()

    class Meta:
        icon = "archive"


class FeaturedRecordsBlock(SectionDepthAwareStructBlock):
    introduction = blocks.CharBlock(max_length=200, required=False)
    items = blocks.ListBlock(FeaturedRecordsItemBlock)

    class Meta:
        icon = "archive"
        template = "articles/blocks/featured_records.html"
        label = "Featured records"


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
    publication_date = blocks.DateBlock(required=False)
    author = blocks.CharBlock(required=False)
    duration = blocks.CharBlock(
        required=False,
        max_length=50,
        label="Duration",
        help_text="Podcast or video duration. Or estimated read time of article.",
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
    description = blocks.RichTextBlock(
        features=settings.INLINE_RICH_TEXT_FEATURES,
        help_text="A description of the promoted page",
    )

    class Meta:
        label = "Featured link"
        template = "articles/blocks/promoted_item.html"
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
    description = blocks.RichTextBlock(
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
    summary = blocks.RichTextBlock(
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
    teaser_image = ImageChooserBlock(
        help_text="An image used to create a teaser for the promoted page"
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


class QuoteBlock(SectionDepthAwareStructBlock):
    """
    A unique version of QuoteBlock for use in multi-level 'section'
    blocks, where the heading element automatically changes to match
    the content depth.
    """

    heading = blocks.CharBlock(required=False, max_length=100)
    quote = blocks.RichTextBlock(
        required=True, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    attribution = blocks.CharBlock(required=False, max_length=100)

    class Meta:
        icon = "openquote"
        label = "Quote"
        template = "articles/blocks/quote.html"


class SubHeadingBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100)

    class Meta:
        icon = "heading"
        label = "Sub-heading"
        template = "articles/blocks/sub_heading.html"


class SectionContentBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    quote = QuoteBlock()
    sub_heading = SubHeadingBlock()
    image = ContentImageBlock()
    media = MediaBlock()
    featured_record = FeaturedRecordBlock()
    featured_records = FeaturedRecordsBlock()
    promoted_item = PromotedItemBlock()
    promoted_list = PromotedListBlock()


class ContentSectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        template = "articles/blocks/section.html"


class ArticlePageStreamBlock(blocks.StreamBlock):
    content_section = ContentSectionBlock()
