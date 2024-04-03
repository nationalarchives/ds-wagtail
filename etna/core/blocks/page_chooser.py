from wagtail import blocks


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
        rendition_size="fill-600x400",
        jpeg_quality=60,
        webp_quality=80,
        **kwargs,
    ):
        self.jpeg_quality = jpeg_quality
        self.webp_quality = webp_quality
        self.rendition_size = rendition_size
        super().__init__(required=required, help_text=help_text, **kwargs)

    def get_api_representation(self, value, context=None):
        if value:
            specific = value.specific

            try:
                jpeg_image = specific.teaser_image.get_rendition(
                    f"{self.rendition_size}|format-jpeg|jpegquality-{self.jpeg_quality}"
                )
                webp_image = specific.teaser_image.get_rendition(
                    f"{self.rendition_size}|format-webp|webpquality-{self.webp_quality}"
                )
            except AttributeError:
                jpeg_image = None
                webp_image = None

            try:
                type_label = specific.type_label()
            except AttributeError:
                type_label = None

            try:
                is_newly_published = specific.is_newly_published
            except AttributeError:
                is_newly_published = None

            return {
                "id": specific.id,
                "title": specific.title,
                "teaser_image_jpeg": (
                    {
                        "url": jpeg_image.url,
                        "full_url": jpeg_image.full_url,
                        "width": jpeg_image.width,
                        "height": jpeg_image.height,
                    }
                    if jpeg_image
                    else None
                ),
                "teaser_image_webp": (
                    {
                        "url": webp_image.url,
                        "full_url": webp_image.full_url,
                        "width": webp_image.width,
                        "height": webp_image.height,
                    }
                    if webp_image
                    else None
                ),
                "type_label": type_label,
                **(
                    {"is_newly_published": is_newly_published}
                    if is_newly_published is not None
                    else {}
                ),
                "url": specific.url,
                "full_url": specific.full_url,
            }
        return None
