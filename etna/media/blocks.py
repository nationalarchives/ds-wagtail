from wagtail import blocks
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

    title = blocks.CharBlock(
        required=True,
        help_text="A descriptive title for the media block",
    )
    background_image = ImageChooserBlock(
        help_text="A background image for the media block"
    )
    media = MediaChooserBlock()

    class Meta:
        template = "media/blocks/media-block.html"
        help_text = "An embedded audio or video block"
        icon = "play"
        label = "Media"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["src"] = value["media"].sources[0]["src"]
        context["type"] = value["media"].sources[0]["type"]
        return context

    @property
    def admin_label(self):
        return self.meta.label
