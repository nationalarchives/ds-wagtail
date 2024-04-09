from wagtail import blocks
from etna.images.models import CustomImage
from django.core import serializers

class APIPageChooserBlock(blocks.PageChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            api_representation = {}
            specific = value.specific
            for field, serializer in specific.get_api_fields().items():
                field_data = getattr(specific, field, None)
                if serializer:
                    field_data = serializer.to_representation(field_data)
                # try:
                #     if callable(field_data):
                #         field_data = field_data()
                #     elif isinstance(field_data, CustomImage):
                #         field_data = field_data.get_rendition("fill-200x200").url
                #     else:
                #         field_data = serializers.serialize("json", field_data)
                # except:
                #     print("error")
                print(field_data)
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
