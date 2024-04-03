from wagtail import blocks

from etna.core.serializers.pages import get_api_fields

class APIPageChooserBlock(blocks.PageChooserBlock):
    """
    APIPageChooserBlock inherits PageChooserBlock and adds the ability
    to generate a JSON representation of the linked page. Without this,
    the API would return the database entry - which is just a page ID.

    This is useful when you want to include a page in a block, and you
    want to display the page data, such as title, URL, teaser image etc.

    We use the specific attribute to ensure that this block works with
    any page type that has a specific attribute, such as type_label.
    If we want to set wagtailcore.Page as the page_type, the Page model
    doesn't have type_label - so will throw an error otherwise (hence the
    try/except blocks).

    The block also allows for the rendition_size, jpeg_quality and webp_quality
    of the teaser image to be set, the same way as the APIImageChooserBlock.
    """

    def __init__(
        self,
        required=True,
        help_text=None,
        api_fields=None,
        **kwargs,
    ):
        self.rendition_size = kwargs.pop("rendition_size", None)
        self.jpeg_quality = kwargs.pop("jpeg_quality", None)
        self.webp_quality = kwargs.pop("webp_quality", None)
        self.api_fields = api_fields or {}
        super().__init__(required=required, help_text=help_text, **kwargs)

    def get_api_representation(self, value, context=None):
        return get_api_fields(value, api_fields=self.api_fields, rendition_size=self.rendition_size, jpeg_quality=self.jpeg_quality, webp_quality=self.webp_quality)
