from wagtail import blocks

from .page_chooser import APIPageChooserBlock


class FeaturedRecordArticleBlock(blocks.StructBlock):
    page = APIPageChooserBlock(
        label="Page",
        page_type="articles.RecordArticlePage",
        required_api_fields=[
            "teaser_text",
            "teaser_image_jpg",
            "teaser_image_webp",
            "teaser_image_large_jpg",
            "teaser_image_large_webp",
            "teaser_image_square_jpg",
            "teaser_image_square_webp",
        ],
    )

    class Meta:
        icon = "doc-empty-inverse"
        template = "blocks/featured_record_article.html"
        label = "Featured record article"
