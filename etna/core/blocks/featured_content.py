from wagtail import blocks

from etna.core.blocks.image import APIImageChooserBlock

from .base import SectionDepthAwareStructBlock
from .page_chooser import APIPageChooserBlock
from .page_list import PageListBlock


class FeaturedRecordArticleBlock(blocks.StructBlock):
    page = APIPageChooserBlock(
        label="Page",
        page_type="articles.RecordArticlePage",
        required_api_fields=[
            "teaser_image",
        ],
    )

    class Meta:
        icon = "doc-empty-inverse"
        template = "blocks/featured_record_article.html"
        label = "Featured record article"


class RelatedItemBlock(SectionDepthAwareStructBlock):
    title = blocks.CharBlock(
        max_length=100,
        help_text="Title of the promoted page",
    )
    description = blocks.TextBlock(
        help_text="A description of the promoted page",
    )
    teaser_image = APIImageChooserBlock(
        help_text="Image that will appear on thumbnails and promos around the site."
    )
    url = blocks.URLBlock(
        label="external URL", help_text="URL for the external page"
    )

    class Meta:
        icon = "link"
        help_text = "Block used promote an external page"
        template = "articles/blocks/related_item.html"


class FeaturedCollectionBlock(SectionDepthAwareStructBlock):
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
        template = "articles/blocks/featured_collection.html"
