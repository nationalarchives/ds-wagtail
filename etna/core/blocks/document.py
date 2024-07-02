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

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)

        file = value.get("file")

        if file:
            if file.file_size >= 1000000:
                file_size = f"{((file.file_size/1024)/1024):.2f}MB"
            else:
                file_size = f"{(file.file_size/1024):.2f}KB"

            representation["file"] = {
                "id": file.id,
                "title": file.title,
                "description": file.description,
                "size": file_size,
                "type": file.file_extension,
                "extent": file.extent,
                "url": file.file.url,
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
