from unittest.mock import patch

from app.ukgwa.blocks import BookmarkletBlock, LinkWithDescriptionBlock
from django.test import SimpleTestCase


def _make_link_representation(**overrides):
    representation = {
        "url": "https://example.com",
        "text": "Example",
        "is_page": False,
        "page_id": None,
        "domain": "example.com",
    }
    representation.update(overrides)
    return representation


class LinkWithDescriptionBlockTests(SimpleTestCase):
    @patch("app.ukgwa.blocks.LinkBlock.get_api_representation")
    def test_get_api_representation_adds_description(self, mock_super_representation):
        mock_super_representation.return_value = _make_link_representation()
        block = LinkWithDescriptionBlock()

        representation = block.get_api_representation(
            {"description": "Helpful summary"}
        )

        self.assertEqual(representation["description"], "Helpful summary")
        self.assertEqual(representation["text"], "Example")

    @patch("app.ukgwa.blocks.LinkBlock.get_api_representation")
    def test_get_api_representation_defaults_missing_description_to_empty_string(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = _make_link_representation()
        block = LinkWithDescriptionBlock()

        representation = block.get_api_representation({})

        self.assertEqual(representation["description"], "")


class BookmarkletBlockTests(SimpleTestCase):
    def test_get_api_representation_returns_true(self):
        block = BookmarkletBlock()

        representation = block.get_api_representation({})

        self.assertIs(representation, True)
