from django.conf import settings

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from ..media.blocks import MediaBlock
from ..paragraphs.blocks import ParagraphWithHeading
from ..quotes.blocks import QuoteBlock
from ..records.blocks import RecordChooserBlock
from ..sections.blocks import SectionBlock

from django.utils.html import format_html

class FeaturedRecordBlock(blocks.StructBlock):
    record = RecordChooserBlock()
    teaser_image = ImageChooserBlock(
        required=False,
        help_text="Add an image to be displayed with the selected record.")

    class Meta:
        icon = "fa-archive"
        template = "insights/blocks/featured_record.html"


class FeaturedRecordsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, required=True, label="Heading (heading level 3)")
    introduction = blocks.CharBlock(max_length=200, required=True)
    records = blocks.ListBlock(
        RecordChooserBlock,
    )

    class Meta:
        icon = "fa-archive"
        template = "insights/blocks/featured_records.html"


class PromotedItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page", label="Title (heading level 3)")
    category = SnippetChooserBlock("categories.Category")
    publication_date = blocks.DateBlock(
        required=False
    )
    duration = blocks.CharBlock(
        required=False,
        max_length=50,
        label="Duration/Read time",
        help_text="Podcast or video duration. Or estimated read time of article."
    )
    url = blocks.URLBlock(label="External URL", help_text="URL for the external page")
    target_blank = blocks.BooleanBlock(label=format_html("%s <p style='font-size: 11px;'>%s</p>" % (
    "Should this URL open in a new tab?",
    "Tick the box if 'yes'"   
    )))
    cta_label = blocks.CharBlock(
        label="Call to action label", max_length=50,
        help_text=format_html("%s <strong>%s</strong>'." % (
    "The text displayed on the button for your URL. If your URL links to an external site, please add the name of the site they will land on, and what they will find on this page. For example 'Watch our short film ",
    "about Shakespeare on YouTube"   
    ))
    )
    teaser_image = ImageChooserBlock(
        help_text="An image used to create a teaser for the promoted page"
    )
    teaser_alt_text = blocks.CharBlock(
        max_length=100, help_text="Alt text of the teaser image"
    )
    description = blocks.RichTextBlock(
        features=settings.INLINE_RICH_TEXT_FEATURES,
        help_text="A description of the promoted page",
    )

    class Meta:
        template = "insights/blocks/promoted_item.html"
        help_text = "Block used promote an external page"
        icon = "fa-star"


class PromotedListItemBlock(blocks.StructBlock):
    """
    Items for promoted list block.
    """

    title = blocks.CharBlock(
        required=True, max_length=100, help_text="Title of the promoted page", label="Heading (heading level 4)"
    )
    description = blocks.RichTextBlock(
        required=False,
        features=settings.INLINE_RICH_TEXT_FEATURES,
        help_text="A description of the promoted page",
    )
    url = blocks.URLBlock(required=True)

    class Meta:
        icon = "fa-external-link"


class PromotedListBlock(blocks.StructBlock):
    """
    Streamfield for collating a series of links for research or interesting pages.
    """

    heading = blocks.CharBlock(required=True, max_length=100, label="Heading (heading level 3)")
    category = SnippetChooserBlock("categories.Category")
    summary = blocks.RichTextBlock(
        required=False, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    promoted_items = blocks.ListBlock(PromotedListItemBlock())

    class Meta:
        icon = "fa-list"
        label = "Promoted item list"
        template = "insights/blocks/promoted_list_block.html"


class RelatedItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page", label="Heading (heading level 3)")
    description = blocks.TextBlock(
        help_text="A description of the promoted page",
    )
    teaser_image = ImageChooserBlock(
        help_text="An image used to create a teaser for the promoted page"
    )
    url = blocks.URLBlock(label="external URL", help_text="URL for the external page")

    class Meta:
        help_text = "Block used promote an external page"
        icon = "fa-external-link"
        template = "insights/blocks/related_item.html"


class RelatedItemsBlock(blocks.StructBlock):
    """
    Items for promoted list block.
    """

    heading = blocks.CharBlock(required=True, max_length=100, label="Heading (heading level 3)")
    description = blocks.CharBlock(required=True, max_length=100)
    related_items = blocks.ListBlock(RelatedItemBlock)

    class Meta:
        icon = "fa-chain"
        template = "insights/blocks/related_items.html"
        block_counts = {
            "related_items": {"min_num": 1, "max_num": 1},
        }


class InsightsIndexPageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphWithHeading()


class InsightsPageStreamBlock(blocks.StreamBlock):
    featured_record = FeaturedRecordBlock()
    featured_records = FeaturedRecordsBlock()
    media = MediaBlock()
    paragraph_with_heading = ParagraphWithHeading()
    promoted_item = PromotedItemBlock()
    promoted_list = PromotedListBlock()
    quote = QuoteBlock()
    related_items = RelatedItemsBlock()
    section = SectionBlock()
