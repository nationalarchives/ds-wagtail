from wagtail import blocks

from .page_chooser import APIPageChooserBlock


class FeaturedRecordArticleBlock(blocks.StructBlock):
    page = APIPageChooserBlock(
        label="Page",
        page_type="wagtailcore.Page",
    )

    class Meta:
        icon = "doc-empty-inverse"
        template = "blocks/featured_record_article.html"
        label = "Featured record article"
