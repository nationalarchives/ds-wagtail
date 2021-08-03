from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from django.template.loader import render_to_string

from wagtail.core import blocks
from wagtailmedia.blocks import ChooserBlock, AbstractMediaChooserBlock


class EtnaMediaBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ""

        context = {
            "value": value,
            "src": value.sources[0]["src"],
            "type": value.sources[0]["type"],
        }

        # Check for empty rich text fields.
        if value.description == "<p></p>":
            value.description = None

        if value.transcript == "<p></p>":
            value.transcript = None

        # Render using the appropriate template.
        if value.type == "audio":
            return render_to_string("media/blocks/media-block--audio.html", context)
        elif value.type == "video":
            return render_to_string("media/blocks/media-block--video.html", context)
        else:
            return ""

    class Meta:
        icon = "fa-play"
