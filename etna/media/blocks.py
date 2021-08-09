from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from django.template.loader import render_to_string

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock


class EtnaMediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        pass


class MediaBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=100, required=True)
    background_image = ImageChooserBlock(
        help_text="A background image for the media block"
    )
    media = EtnaMediaBlock()

    class Meta:
        template = "media/blocks/media-block.html"
        help_text = "An embedded audio or video block"
        icon = "fa-play"
