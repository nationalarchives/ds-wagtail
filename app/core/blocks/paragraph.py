from django.conf import settings
from wagtail import blocks
from wagtail.rich_text import expand_db_html


class APIRichTextBlock(blocks.RichTextBlock):
    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        return expand_db_html(representation)


class ParagraphBlock(blocks.StructBlock):
    text = APIRichTextBlock(features=settings.RESTRICTED_RICH_TEXT_FEATURES)

    class Meta:
        icon = "paragraph"
        label = "Paragraph text"
