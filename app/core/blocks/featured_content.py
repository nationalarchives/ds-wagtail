from wagtail import blocks

from .page_list import PageListBlock


class FeaturedCollectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100)
    description = blocks.TextBlock(max_length=200)
    items = PageListBlock(
        "articles.ArticlePage",
        "articles.RecordArticlePage",
        "articles.FocusedArticlePage",
        exclude_drafts=True,
        exclude_private=True,
        select_related=["teaser_image"],
        min_num=3,
        max_num=9,
    )

    class Meta:
        icon = "list"
        label = "Featured pages"
