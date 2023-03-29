from wagtail import blocks

from etna.core.blocks import PromotedLinkBlock


class CollectionHighlightsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="Collection Highlights")

    class Meta:
        template = "collections/blocks/collection_highlights.html"
        help_text = "Block used to output the list of collection highlights"
        icon = "th"


class FeaturedPageBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100)
    description = blocks.CharBlock(
        required=False, max_length=200, help_text="A description of the featured page"
    )
    page = blocks.PageChooserBlock()

    class Meta:
        template = "collections/blocks/featured_page.html"
        help_text = "Block used feature a page from within Wagtail"
        icon = "arrow-up"


class PromotedPagesBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100)
    sub_heading = blocks.CharBlock(max_length=200)
    promoted_items = blocks.ListBlock(PromotedLinkBlock, min=3, max=3)

    class Meta:
        template = "collections/blocks/promoted_pages.html"
        help_text = "Block used promote external pages"
        icon = "th-large"


class TopicExplorerIndexBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="Explore by topic")
    page = blocks.PageChooserBlock(page_type="collections.TopicExplorerIndexPage")

    class Meta:
        template = "collections/blocks/topic_explorer.html"
        help_text = "Outputs all topic child pages"
        icon = "th-large"


class TimePeriodExplorerIndexBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, default="Explore by time period")
    page = blocks.PageChooserBlock(page_type="collections.TimePeriodExplorerIndexPage")

    class Meta:
        template = "collections/blocks/time_period_explorer.html"
        help_text = "Outputs all time period child pages"
        icon = "th-large"


class ExplorerIndexPageStreamBlock(blocks.StreamBlock):
    time_period_explorer_index = TimePeriodExplorerIndexBlock()
    topic_explorer_index = TopicExplorerIndexBlock()

    class Meta:
        block_counts = {
            "time_period_explorer_index": {"min_num": 1, "max_num": 1},
            "topic_explorer_index": {"min_num": 1, "max_num": 1},
        }


class TimePeriodExplorerPageStreamBlock(blocks.StreamBlock):
    collection_highlights = CollectionHighlightsBlock()
    promoted_pages = PromotedPagesBlock()

    class Meta:
        block_counts = {
            "collection_highlights": {"min_num": 1, "max_num": 1},
            "promoted_pages": {"max_num": 1},
        }


class TimePeriodExplorerIndexPageStreamBlock(blocks.StreamBlock):
    topic_explorer_index = TopicExplorerIndexBlock()

    class Meta:
        block_counts = {
            "topic_explorer_index": {"min_num": 1, "max_num": 1},
        }


class TopicExplorerPageStreamBlock(blocks.StreamBlock):
    collection_highlights = CollectionHighlightsBlock()
    promoted_pages = PromotedPagesBlock()

    class Meta:
        block_counts = {
            "collection_highlights": {"min_num": 1, "max_num": 1},
            "promoted_pages": {"max_num": 1},
        }


class TopicExplorerIndexPageStreamBlock(blocks.StreamBlock):
    time_period_explorer_index = TimePeriodExplorerIndexBlock()

    class Meta:
        block_counts = {
            "time_period_explorer_index": {"min_num": 1, "max_num": 1},
        }
