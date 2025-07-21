from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock


class DocumentBlock(blocks.StructBlock):
    """
    A block for embedding a document file in a page.
    """

    file = DocumentChooserBlock(required=True)

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)

        file = value.get("file")

        if file:
            representation["file"] = {
                "id": file.id,
                "title": file.title,
                "description": file.description or None,
                "file_size": file.file_size,
                "pretty_file_size": file.pretty_file_size,
                "type": file.file_extension,
                "extent": file.extent,
                "file_location": file.file.url,
                "url": file.url,
            }

        return representation

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
