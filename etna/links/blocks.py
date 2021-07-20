from django.conf import settings

from wagtail.core import blocks
from wagtail.core.fields import RichTextField
from wagtail.snippets.blocks import ChooserBlock, SnippetChooserBlock


class LinkItemBlock(blocks.StructBlock):
    """
    Link items for link list block.
    """
    heading = blocks.CharBlock(required=True, max_length=100)
    summary = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)
    url = blocks.URLBlock(required=True)

    class Meta:
        icon = 'fa-external-link'


class LinkListBlock(blocks.StructBlock):
    """
    Streamfield for collating a series of links for research or interesting pages.
    """
    heading = blocks.CharBlock(required=True, max_length=100)
    category = SnippetChooserBlock('categories.Category')
    summary = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)
    link_list = blocks.ListBlock(LinkItemBlock(), label='Links')

    class Meta:
        icon = 'fa-list'
        label = 'Link list'
        template = 'links/blocks/link-list-block.html'
