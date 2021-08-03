from django.conf import settings

from wagtail.core import blocks
from wagtail.snippets.blocks import SnippetChooserBlock


class AuthorBlock(blocks.StructBlock):
    author = SnippetChooserBlock("authors.Author")

    class Meta:
        icon = "fa-user-circle "
        template = "authors/blocks/author.html"
