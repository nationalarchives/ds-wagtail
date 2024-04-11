from wagtail import blocks
from etna.core.serializers.pages import get_api_data

class APIPageChooserBlock(blocks.PageChooserBlock):
    def __init__(
        self, page_type=None, can_choose_root=False, target_model=None, required_api_fields=[], **kwargs
    ):
        self.required_api_fields = required_api_fields
        super().__init__(**kwargs)

    def get_api_representation(self, value, context=None):
        return get_api_data(object=value.specific, required_api_fields=self.required_api_fields)

class FeaturedRecordArticleBlock(blocks.StructBlock):
    page = APIPageChooserBlock(
        label="Page",
        page_type="articles.RecordArticlePage",
        required_api_fields=[
            "title",
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
