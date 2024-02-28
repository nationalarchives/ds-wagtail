from etna.core.blocks import PageListBlock, ParagraphBlock
from wagtail import blocks


class EventPageBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()


class WhatsOnPromotedLinksBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    promoted_links = PageListBlock(min_num=1, max_num=3)

    class Meta:
        template = "blocks/whats_on_promoted_links.html"
        icon = "list"


class RelatedArticlesBlock(blocks.StreamBlock):
    pages = PageListBlock(
        "articles.ArticlePage",
        "articles.RecordArticlePage",
        "articles.FocusedArticlePage",
        exclude_drafts=True,
        exclude_private=True,
        select_related=["teaser_image"],
    )

    class Meta:
        icon = "list"
        label = "Related articles"
        template = "collections/blocks/featured_articles.html"
