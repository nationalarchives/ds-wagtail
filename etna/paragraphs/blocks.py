from django.conf import settings

from wagtail.core import blocks


class ParagraphWithTitleAndImage(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=100)
    paragraph = blocks.RichTextBlock(required=True, features=settings.IMAGE_EMBED_RICH_TEXT_FEATURES)

    class Meta:
        icon = 'fa-paragraph'
        label = 'Paragraph with image'
        template = 'paragraphs/blocks/paragraph-with-title-and-image.html'
