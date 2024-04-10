from wagtail import blocks

def get_api_fields(object, required_api_fields:list=None) -> list:
    """
    Get the selected fields (required_api_fields) from the object's api_fields
    attribute, and return them as a dictionary with the field name as the key,
    and the serializer as the value.
    """
    fields = []
    if api_fields := object.api_fields:
        for field in required_api_fields:
            for api_field in api_fields:
                if field == api_field.name:
                    fields.append(api_field)
                    break
    return fields

def get_api_data(object, required_api_fields:list=None) -> dict:
    if object:
        api_representation = {}
        specific = object.specific
        if api_fields := get_api_fields(object=specific, required_api_fields=required_api_fields):
            for field in api_fields:
                field_data = getattr(specific, field.name, None)
                if serializer := field.serializer:
                    if source := serializer.source:
                        field_data = serializer.to_representation(getattr(specific, source, None))
                    else:
                        field_data = serializer.to_representation(field_data)
                if callable(field_data):
                    field_data = field_data()
                api_representation[field.name] = field_data
    return api_representation

class APIPageChooserBlock(blocks.PageChooserBlock):
    def get_api_representation(self, value, context=None):
        return get_api_data(object=value.specific, required_api_fields=["type_label",
        "teaser_image_jpg",
        "teaser_image_webp",
        "teaser_image_large_jpg",
        "teaser_image_large_webp",
        "teaser_image_square_jpg",
        "teaser_image_square_webp",
        "tags"])

class FeaturedRecordArticleBlock(blocks.StructBlock):
    page = APIPageChooserBlock(
        label="Page",
        page_type="wagtailcore.Page",
    )

    class Meta:
        icon = "doc-empty-inverse"
        template = "blocks/featured_record_article.html"
        label = "Featured record article"
