from wagtail import blocks

from app.core.blocks import LargeCardLinksBlock, PageListBlock, PromotedLinkBlock


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
        template = "collections/blocks/featured_articles.html"
