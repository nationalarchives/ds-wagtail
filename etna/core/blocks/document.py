from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock


class DocumentBlock(blocks.StructBlock):
    """
    A block for embedding a document file in a page.
    """

    link_text = blocks.CharBlock(
        required=True,
        help_text="The text to display for the link to the document",
    )
    file = DocumentChooserBlock(required=True)

    class Meta:
        icon = "doc-full"
        label = "Document"

class DocumentsBlock(blocks.StructBlock):
    """
    A block for embedding multiple document files in a page.
    """

    documents = blocks.ListBlock(DocumentBlock())

    class Meta:
        icon = "doc-full"
        label = "Documents"