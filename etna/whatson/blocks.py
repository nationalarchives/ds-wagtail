from wagtail import blocks

from etna.core.blocks import PageListBlock, ParagraphBlock


class EventPageBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()


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
