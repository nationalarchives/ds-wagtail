from wagtail import blocks

class APIPageChooserBlock(blocks.PageChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            api_representation = {}
            specific = value.specific
            for field in specific.get_api_fields():
                field_data = getattr(specific, field, None)
                if callable(field_data):
                    field_data = field_data()
                api_representation[field] = field_data
        return api_representation

class FeaturedRecordArticleBlock(blocks.StructBlock):
    page = APIPageChooserBlock(
        label="Page",
        page_type="wagtailcore.Page",
    )

    class Meta:
        icon = "doc-empty-inverse"
        template = "blocks/featured_record_article.html"
        label = "Featured record article"
