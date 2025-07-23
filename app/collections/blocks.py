from wagtail import blocks

from app.core.blocks import LargeCardLinksBlock, PageListBlock


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


class FeaturedArticlesBlock(blocks.StructBlock):
    items = PageListBlock(
        "articles.ArticlePage",
        "articles.RecordArticlePage",
        "articles.FocusedArticlePage",
        exclude_drafts=True,
        exclude_private=True,
        select_related=["teaser_image"],
        min_num=3,
        max_num=6,
    )

    class Meta:
        icon = "list"
        label = "Featured articles"
