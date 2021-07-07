from wagtail.core import blocks

from .fields import BASIC_RICH_TEXT_FEATURES


class BasicRichTextBlock(blocks.RichTextBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.features = BASIC_RICH_TEXT_FEATURES

    class Meta:
        icon = "fa-paragraph"
        template = "richtexts/blocks/paragraph.html"
