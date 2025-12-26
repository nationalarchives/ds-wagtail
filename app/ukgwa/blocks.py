from django.utils.translation import gettext_lazy as _
from wagtail import blocks


class ExternalLinkBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="URL")
    link_text = blocks.CharBlock()

    class Meta:
        label = _("External link")
        icon = "link"
