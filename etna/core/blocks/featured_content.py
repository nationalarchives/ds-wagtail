from wagtail import blocks


class FeaturedRecordArticleBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(
        label="Page",
        page_type="articles.RecordArticlePage",
    )

    class Meta:
        icon = "doc-empty-inverse"
        template = "blocks/featured_record_article.html"
        label = "Featured record article"
