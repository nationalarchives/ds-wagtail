from django.conf import settings
from django.utils.html import mark_safe, escape

from wagtail.core import blocks


class ParagraphWithHeading(blocks.StructBlock):
    """
    Paragraph with heading streamfield component.
    """

    heading_tags = [
        ('h2', 'Heading level 2'),
        ('h3', 'Heading level 3'),
        ('h4', 'Heading level 4')
    ]

    heading_level = blocks.ChoiceBlock(
        required=True,
        choices=heading_tags,
        help_text=mark_safe("%s <a href=%s target=%s>%s</a>" % (
            escape(
                "Use this field to select the appropriate heading tag. "
                "Check where this component will sit in the page to ensure "
                "that it follows the correct heading order and avoids skipping levels "
                "e.g. an <h4> should not follow an <h2>. For further information, see:"
            ),
            escape("https://www.w3.org/WAI/tutorials/page-structure/headings"),
            escape("_blank"),
            escape("https://www.w3.org/WAI/tutorials/page-structure/headings/")
        )),
        default="h2"
    )
    heading = blocks.CharBlock(required=True, max_length=100)
    paragraph = blocks.RichTextBlock(required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES)

    class Meta:
        icon = 'fa-paragraph'
        label = 'Paragraph with heading'
        template = 'paragraphs/blocks/paragraph-with-heading.html'
