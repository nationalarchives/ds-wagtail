from django.conf import settings

from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


class AuthorBlock(blocks.StructBlock):
    name = blocks.CharBlock(required=True, max_length=100)
    role = blocks.CharBlock(required=False, max_length=100)
    summary = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)
    image = ImageChooserBlock(required=False)
    bio_link = blocks.URLBlock(required=True, help_text="Link to external bio page")
    bio_link_label = blocks.CharBlock(required=True, help_text="Button text for bio link", max_length=50)

    class Meta:
        icon = "fa-user-circle "
        template = "insights/blocks/author.html"
