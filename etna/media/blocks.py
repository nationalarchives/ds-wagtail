from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock

from wagtailmedia.blocks import AbstractMediaChooserBlock


class MediaChooserBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        """
        AbstractMediaChooserBlock requires this method to be defined
        even though it is only called if no template is specified.

        https://github.com/wagtail/wagtail/blob/8413d00bdd03c447900019961d604186e17d2870/wagtail/core/blocks/base.py#L206
        """
        pass


class MediaBlock(blocks.StructBlock):
    """
    Embedded media block with a selectable background image.
    """
    background_image = ImageChooserBlock(
        help_text="A background image for the media block"
    )
    media = MediaChooserBlock()

    class Meta:
        template = "media/blocks/media-block.html"
        help_text = "An embedded audio or video block"
        icon = "fa-play"

class ImageBlock(blocks.StructBlock):
    """
    An image block which supports accessibility-first design.
    """
    image = ImageChooserBlock(required=True)
    decorative = blocks.BooleanBlock(label="Is this image decorative?")
    alt_text = blocks.CharBlock(max_length=100, help_text="Guidance for alt text.")
    caption = blocks.CharBlock(help_text="An optional caption which will be displayed below the image.", label="Caption (Optional)")

    class Meta:
        template = "media/blocks/image-block.html"
        help_text = "An image block which supports accessibility-first design."
        icon = "fa-image"