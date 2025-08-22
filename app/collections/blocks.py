from wagtail import blocks

from app.core.blocks import LargeCardLinksBlock


class ExplorerIndexPageStreamBlock(blocks.StreamBlock):
    large_card_links = LargeCardLinksBlock()

    class Meta:
        block_counts = {
            "large_card_links": {"max_num": 1},
        }


class TopicIndexPageStreamBlock(blocks.StreamBlock):
    large_card_links = LargeCardLinksBlock()

    class Meta:
        block_counts = {
            "large_card_links": {"max_num": 1},
        }
