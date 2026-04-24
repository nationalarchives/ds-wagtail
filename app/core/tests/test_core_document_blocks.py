from types import SimpleNamespace
from unittest.mock import patch

from app.core.blocks.document import DocumentBlock
from django.test import SimpleTestCase


class DocumentBlockTests(SimpleTestCase):
    @staticmethod
    def _make_document(**overrides):
        defaults = dict(
            id=1,
            title="Guide",
            description="Helpful document",
            file_size=4096,
            pretty_file_size="4kB",
            file_extension="pdf",
            extent="4 pages",
            url="/documents/guide.pdf",
        )
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_replaces_file_with_document_metadata(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = {"file": "placeholder"}
        document = self._make_document(id=7)
        block = DocumentBlock()

        representation = block.get_api_representation({"file": document})

        self.assertEqual(
            representation["file"],
            {
                "id": 7,
                "title": "Guide",
                "description": "Helpful document",
                "file_size": 4096,
                "pretty_file_size": "4kB",
                "type": "pdf",
                "extent": "4 pages",
                "url": "/documents/guide.pdf",
            },
        )

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_without_file_leaves_representation_unchanged(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = {"file": None}
        block = DocumentBlock()

        representation = block.get_api_representation({"file": None})

        self.assertIsNone(representation["file"])

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_coerces_empty_description_to_none(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = {"file": "placeholder"}
        document = self._make_document(
            description="", file_size=100, pretty_file_size="100B", extent=None
        )
        block = DocumentBlock()

        representation = block.get_api_representation({"file": document})

        self.assertIsNone(representation["file"]["description"])
