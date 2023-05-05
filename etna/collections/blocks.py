from wagtail import blocks

from etna.core.blocks import LargeCardLinksBlock, PromotedLinkBlock


class PromotedPagesBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100)
    sub_heading = blocks.CharBlock(max_length=200)
    promoted_items = blocks.ListBlock(PromotedLinkBlock, min=3, max=3)

    class Meta:
        template = "collections/blocks/promoted_pages.html"
        help_text = "Block used to promote external pages"
        icon = "th-large"


class ExplorerIndexPageStreamBlock(blocks.StreamBlock):
    large_card_links = LargeCardLinksBlock()

    class Meta:
        block_counts = {
            "large_card_links": {"max_num": 1},
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
