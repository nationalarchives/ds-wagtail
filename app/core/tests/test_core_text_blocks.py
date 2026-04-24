from unittest.mock import patch

from app.core.blocks.code import CodeBlock
from app.core.blocks.paragraph import APIRichTextBlock
from app.core.blocks.quote import QuoteBlock, ReviewBlock
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from wagtail.rich_text import RichText


def _make_code_value(**overrides):
    value = {
        "filename": "",
        "language": "",
        "code": "print('hello')",
        "allow_copying": True,
    }
    value.update(overrides)
    return value


def _make_quote_representation(
    citation="Source title",
    citation_internal_link=None,
    citation_external_link="",
):
    return {
        "quote": "Quote text",
        "attribution": "Author",
        "source": {
            "citation": citation,
            "source_link": {
                "citation_internal_link": citation_internal_link,
                "citation_external_link": citation_external_link,
            },
        },
    }


def _make_review_representation(stars):
    return {
        "quote": "Loved it",
        "attribution": "Reviewer",
        "stars": stars,
    }


class APIRichTextBlockTests(SimpleTestCase):
    @patch("app.core.blocks.paragraph.expand_db_html", return_value="<p>Expanded</p>")
    def test_get_api_representation_expands_database_html(self, mock_expand_db_html):
        block = APIRichTextBlock()

        representation = block.get_api_representation(RichText("<p>Stored</p>"))

        self.assertEqual(representation, "<p>Expanded</p>")
        mock_expand_db_html.assert_called_once_with("<p>Stored</p>")


class CodeBlockTests(SimpleTestCase):
    def test_get_api_representation_omits_empty_optional_fields(self):
        block = CodeBlock()

        representation = block.get_api_representation(_make_code_value())

        self.assertEqual(
            representation,
            {
                "code": "print('hello')",
                "allow_copying": True,
            },
        )

    def test_get_api_representation_includes_language_and_filename_when_present(self):
        block = CodeBlock()

        representation = block.get_api_representation(
            _make_code_value(
                filename="hello.py",
                language="python",
                allow_copying=False,
            )
        )

        self.assertEqual(
            representation,
            {
                "code": "print('hello')",
                "allow_copying": False,
                "language": "python",
                "filename": "hello.py",
            },
        )


class QuoteBlockTests(SimpleTestCase):
    @patch("wagtail.blocks.StructBlock.clean")
    def test_clean_rejects_internal_and_external_citation_links(self, mock_super_clean):
        value = {
            "source": {
                "source_link": {
                    "citation_internal_link": object(),
                    "citation_external_link": "https://example.com/source",
                }
            }
        }
        mock_super_clean.return_value = value
        block = QuoteBlock()

        with self.assertRaises(ValidationError) as context:
            block.clean(value)

        self.assertIn(
            "either a page link or an external link, not both", str(context.exception)
        )

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_prefers_external_citation_url(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = _make_quote_representation(
            citation_internal_link={"full_url": "https://example.com/internal"},
            citation_external_link="https://example.com/external",
        )
        block = QuoteBlock()

        representation = block.get_api_representation({})

        self.assertEqual(
            representation,
            {
                "quote": "Quote text",
                "attribution": "Author",
                "citation": "Source title",
                "citation_url": "https://example.com/external",
            },
        )

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_falls_back_to_internal_citation_url(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = _make_quote_representation(
            citation_internal_link={"full_url": "/about/"},
        )
        block = QuoteBlock()

        representation = block.get_api_representation({})

        self.assertEqual(representation["citation_url"], "/about/")

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_returns_none_citation_url_when_no_links(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = _make_quote_representation(
            citation=None,
        )
        block = QuoteBlock()

        representation = block.get_api_representation({})

        self.assertIsNone(representation["citation_url"])


class ReviewBlockTests(SimpleTestCase):
    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_casts_stars_to_int(self, mock_super_representation):
        mock_super_representation.return_value = _make_review_representation("5")
        block = ReviewBlock()

        representation = block.get_api_representation({"stars": "5"})

        self.assertEqual(representation["stars"], 5)

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_casts_zero_stars_to_int(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = _make_review_representation("0")
        block = ReviewBlock()

        representation = block.get_api_representation({"stars": "0"})

        self.assertEqual(representation["stars"], 0)
