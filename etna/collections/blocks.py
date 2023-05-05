from wagtail import blocks

from etna.core.blocks import LargeCardLinksBlock, PromotedLinkBlock

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
    promoted_pages = PromotedPagesBlock()

    class Meta:
        block_counts = {
            "promoted_pages": {"max_num": 1},
        }


class TopicExplorerPageStreamBlock(blocks.StreamBlock):
    promoted_pages = PromotedPagesBlock()

    class Meta:
        block_counts = {
            "promoted_pages": {"max_num": 1},
        }


class TopicIndexPageStreamBlock(blocks.StreamBlock):
    large_card_links = LargeCardLinksBlock()

    class Meta:
        block_counts = {
            "large_card_links": {"max_num": 1},
        }
