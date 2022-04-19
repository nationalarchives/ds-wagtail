from django.conf import settings
from django.utils.html import format_html

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from etna.core.blocks import (
    ContentImageBlock,
    ImageBlock,
    PageListBlock,
    ParagraphBlock,
    ParagraphWithHeading,
    NoCaptionImageBlock,
    SectionDepthAwareStructBlock,
)

from ..media.blocks import MediaBlock
from ..records.blocks import RecordChooserBlock


class FeaturedRecordBlock(SectionDepthAwareStructBlock):
    record = RecordChooserBlock()
    image = ImageBlock(
        label="Teaser image",
        required=False,
        help_text="Add an image to be displayed with the selected record.",
        template="insights/blocks/images/blog-embed__image-container.html",
    )

    class Meta:
        icon = "archive"
        template = "insights/blocks/featured_record.html"


class FeaturedRecordsBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, required=True)
    introduction = blocks.CharBlock(max_length=200, required=True)
    records = blocks.ListBlock(
        RecordChooserBlock,
    )

    class Meta:
        icon = "archive"
        template = "insights/blocks/featured_records.html"


class PromotedItemBlock(SectionDepthAwareStructBlock):
    title = blocks.CharBlock(
        max_length=100,
        help_text="Title of the promoted page",
        label="Title",
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
        template="insights/blocks/images/blog-embed__image-container.html",
    )
    description = blocks.RichTextBlock(
        features=settings.INLINE_RICH_TEXT_FEATURES,
        help_text="A description of the promoted page",
    )

    class Meta:
        template = "insights/blocks/promoted_item.html"
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
        help_text="Title of the promoted page",
        label="Heading",
    )
    description = blocks.RichTextBlock(
        required=False,
        features=settings.INLINE_RICH_TEXT_FEATURES,
        help_text="A description of the promoted page",
    )
    url = blocks.URLBlock(required=True)

    class Meta:
        icon = "star"


class PromotedListBlock(SectionDepthAwareStructBlock):
    """
    Streamfield for collating a series of links for research or interesting pages.
    """

    heading = blocks.CharBlock(required=True, max_length=100)
    category = SnippetChooserBlock("categories.Category")
    summary = blocks.RichTextBlock(
        required=False, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    promoted_items = blocks.ListBlock(PromotedListItemBlock())

    class Meta:
        icon = "list"
        label = "Promoted item list"
        template = "insights/blocks/promoted_list_block.html"


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
        template = "insights/blocks/related_item.html"


class RelatedItemsBlock(SectionDepthAwareStructBlock):
    """
    Items for promoted list block.
    """

    heading = blocks.CharBlock(required=True, max_length=100)
    description = blocks.CharBlock(required=True, max_length=100)
    related_items = blocks.ListBlock(RelatedItemBlock)

    class Meta:
        icon = "external-link-alt"
        template = "insights/blocks/related_items.html"
        block_counts = {
            "related_items": {"min_num": 1, "max_num": 1},
        }


class FeaturedCollectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100)
    description = blocks.TextBlock(max_length=200)
    items = PageListBlock(
        "insights.InsightsPage",
        exclude_drafts=True,
        exclude_private=False,
        select_related=["teaser_image"],
        min_num=3,
        max_num=9,
    )

    class Meta:
        icon = "list"
        label = "Featured collection"
        template = "insights/blocks/featured_collection.html"


class InsightsIndexPageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphWithHeading()


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
        template = "insights/blocks/quote.html"


class SubHeadingBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100)

    class Meta:
        icon = "heading"
        label = "Sub-heading"
        template = "insights/blocks/sub_heading.html"


class SubSectionContentBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
    quote = QuoteBlock()
    sub_heading = SubHeadingBlock()
    image = ContentImageBlock()
    media = MediaBlock()


class ContentSubSectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SubSectionContentBlock()

    class Meta:
        label = "Sub-section"
        template = "insights/blocks/section.html"


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
    related_items = RelatedItemsBlock()
    content_sub_section = ContentSubSectionBlock()


class ContentSectionBlock(SectionDepthAwareStructBlock):
    heading = blocks.CharBlock(max_length=100, label="Heading")
    content = SectionContentBlock(required=False)

    class Meta:
        label = "Section"
        template = "insights/blocks/section.html"


class InsightsPageStreamBlock(blocks.StreamBlock):
    content_section = ContentSectionBlock()
