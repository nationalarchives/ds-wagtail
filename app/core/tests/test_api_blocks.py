from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.core.blocks.code import CodeBlock
from app.core.blocks.cta import ButtonBlock
from app.core.blocks.document import DocumentBlock
from app.core.blocks.image import (
    APIImageChooserBlock,
    ImageGalleryBlock,
    PartnerLogoChooserBlock,
)
from app.core.blocks.links import (
    InternalLinkBlock,
    LinkBlock,
    LinkColumnWithHeaderBlock,
)
from app.core.blocks.lists import PeopleListingBlock
from app.core.blocks.page_chooser import APIPageChooserBlock
from app.core.blocks.paragraph import APIRichTextBlock
from app.core.blocks.promoted_links import FeaturedPageBlock
from app.core.blocks.quote import QuoteBlock, ReviewBlock
from app.core.blocks.shop import ShopCollectionBlock
from app.core.serializers import DefaultPageSerializer
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.rich_text import RichText


class APIRichTextBlockTests(SimpleTestCase):
    @patch("app.core.blocks.paragraph.expand_db_html", return_value="<p>Expanded</p>")
    def test_get_api_representation_expands_database_html(self, mock_expand_db_html):
        block = APIRichTextBlock()

        representation = block.get_api_representation(RichText("<p>Stored</p>"))

        self.assertEqual(representation, "<p>Expanded</p>")
        mock_expand_db_html.assert_called_once_with("<p>Stored</p>")


class APIImageChooserBlockTests(SimpleTestCase):
    @patch("app.core.blocks.image.DetailedImageSerializer")
    def test_get_api_representation_uses_detailed_image_serializer(
        self, mock_serializer_class
    ):
        image = object()
        serializer = mock_serializer_class.return_value
        serializer.to_representation.return_value = {"id": 1}
        block = APIImageChooserBlock(
            rendition_size="original",
            jpeg_quality=90,
            webp_quality=80,
            background_colour="000",
        )

        representation = block.get_api_representation(image)

        self.assertEqual(representation, {"id": 1})
        mock_serializer_class.assert_called_once_with(
            rendition_size="original",
            jpeg_quality=90,
            webp_quality=80,
            background_colour="000",
        )
        serializer.to_representation.assert_called_once_with(image)


class ImageGalleryBlockTests(SimpleTestCase):
    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_adds_image_count(self, mock_super_representation):
        mock_super_representation.return_value = {"title": "Gallery"}
        block = ImageGalleryBlock()
        value = {"images": [object(), object(), object()]}

        representation = block.get_api_representation(value)

        self.assertEqual(representation["count"], 3)
        self.assertEqual(representation["title"], "Gallery")


class PartnerLogoChooserBlockTests(SimpleTestCase):
    @patch("app.core.blocks.image.PartnerLogoSerializer")
    def test_get_api_representation_uses_partner_logo_serializer(
        self, mock_serializer_class
    ):
        logo = object()
        serializer = mock_serializer_class.return_value
        serializer.to_representation.return_value = {"name": "Partner"}
        block = PartnerLogoChooserBlock()

        representation = block.get_api_representation(logo)

        self.assertEqual(representation, {"name": "Partner"})
        serializer.to_representation.assert_called_once_with(logo)


class APIPageChooserBlockTests(SimpleTestCase):
    @patch("app.core.blocks.page_chooser.get_api_data")
    def test_get_api_representation_passes_required_api_fields(self, mock_get_api_data):
        page = object()
        mock_get_api_data.return_value = {"teaser_image": {"id": 1}}
        block = APIPageChooserBlock(required_api_fields=["teaser_image"])

        representation = block.get_api_representation(page)

        self.assertEqual(representation, {"teaser_image": {"id": 1}})
        mock_get_api_data.assert_called_once_with(
            object=page,
            required_api_fields=["teaser_image"],
        )


class ButtonBlockTests(SimpleTestCase):
    @patch("wagtail.blocks.StructBlock.clean")
    def test_clean_rejects_both_page_and_external_link(self, mock_super_clean):
        value = {
            "label": "Read more",
            "link": object(),
            "external_link": "https://example.com",
            "accented": False,
        }
        mock_super_clean.return_value = value
        block = ButtonBlock()

        with self.assertRaises(ValidationError) as context:
            block.clean(value)

        self.assertIn(
            "either a page link or an external link, not both", str(context.exception)
        )

    @patch("wagtail.blocks.StructBlock.clean")
    def test_clean_requires_a_link(self, mock_super_clean):
        value = {
            "label": "Read more",
            "link": None,
            "external_link": "",
            "accented": False,
        }
        mock_super_clean.return_value = value
        block = ButtonBlock()

        with self.assertRaises(ValidationError) as context:
            block.clean(value)

        self.assertIn(
            "You must provide either a page link or an external link",
            str(context.exception),
        )

    def test_get_api_representation_prefers_external_link_and_defaults_accent(self):
        block = ButtonBlock()
        value = {
            "label": "Visit",
            "link": SimpleNamespace(full_url="https://example.com/internal"),
            "external_link": "https://example.com/external",
            "accented": None,
        }

        representation = block.get_api_representation(value)

        self.assertEqual(
            representation,
            {
                "label": "Visit",
                "href": "https://example.com/external",
                "accent": False,
            },
        )


class LinkBlockTests(SimpleTestCase):
    def test_link_block_clean_requires_one_link_target(self):
        value = {"page": None, "title": "", "external_link": ""}
        block = LinkBlock()

        with self.assertRaises(StructBlockValidationError) as context:
            block.clean(value)

        self.assertIn("page", context.exception.block_errors)
        self.assertIn("external_link", context.exception.block_errors)

    def test_link_block_clean_requires_title_for_external_link(self):
        value = {
            "page": None,
            "title": "",
            "external_link": "https://www.nationalarchives.gov.uk",
        }
        block = LinkBlock()

        with self.assertRaises(StructBlockValidationError) as context:
            block.clean(value)

        self.assertIn("title", context.exception.block_errors)

    def test_internal_link_get_api_representation_uses_struct_value_helpers(self):
        block = InternalLinkBlock()
        value = Mock()
        value.url.return_value = "/visit-us"
        value.text.return_value = "Visit us"
        value.is_page.return_value = True
        value.page_id.return_value = 42
        value.external_domain.return_value = ""

        representation = block.get_api_representation(value)

        self.assertEqual(
            representation,
            {
                "url": "/visit-us",
                "text": "Visit us",
                "is_page": True,
                "page_id": 42,
                "domain": "",
            },
        )

    def test_link_block_get_api_representation_includes_external_domain(self):
        block = LinkBlock()
        value = block.to_python(
            {
                "page": None,
                "title": "The National Archives",
                "external_link": "https://www.nationalarchives.gov.uk/explore",
            }
        )

        representation = block.get_api_representation(value)

        self.assertEqual(
            representation["url"], "https://www.nationalarchives.gov.uk/explore"
        )
        self.assertEqual(representation["text"], "The National Archives")
        self.assertFalse(representation["is_page"])
        self.assertIsNone(representation["page_id"])
        self.assertEqual(representation["domain"], "www.nationalarchives.gov.uk")


class LinkColumnWithHeaderBlockTests(SimpleTestCase):
    def test_get_api_representation_flattens_link_values(self):
        block = LinkColumnWithHeaderBlock()
        first_link = Mock()
        first_link.url.return_value = "/one"
        first_link.text.return_value = "One"
        first_link.is_page.return_value = True
        second_link = Mock()
        second_link.url.return_value = "https://example.com/two"
        second_link.text.return_value = "Two"
        second_link.is_page.return_value = False

        representation = block.get_api_representation(
            {"heading": "Resources", "links": [first_link, second_link]}
        )

        self.assertEqual(
            representation,
            {
                "heading": "Resources",
                "links": [
                    {"url": "/one", "text": "One", "is_page": True},
                    {
                        "url": "https://example.com/two",
                        "text": "Two",
                        "is_page": False,
                    },
                ],
            },
        )


class CodeBlockTests(SimpleTestCase):
    def test_get_api_representation_omits_empty_optional_fields(self):
        block = CodeBlock()

        representation = block.get_api_representation(
            {
                "filename": "",
                "language": "",
                "code": "print('hello')",
                "allow_copying": True,
            }
        )

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
            {
                "filename": "hello.py",
                "language": "python",
                "code": "print('hello')",
                "allow_copying": False,
            }
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


class LinkValidationMixinTests(SimpleTestCase):
    @patch("wagtail.blocks.StructBlock.clean")
    def test_clean_rejects_both_page_and_external_link(self, mock_super_clean):
        value = {
            "page": object(),
            "title": "Both set",
            "external_link": "https://example.com",
        }
        mock_super_clean.return_value = value
        block = LinkBlock()

        with self.assertRaises(StructBlockValidationError) as context:
            block.clean(value)

        self.assertIn("page", context.exception.block_errors)
        self.assertIn("external_link", context.exception.block_errors)


class QuoteBlockTests(SimpleTestCase):
    @staticmethod
    def _make_quote_super_return(
        citation="Source title",
        citation_internal_link=None,
        citation_external_link="",
    ):
        """Build the dict that StructBlock.get_api_representation returns; vary only citation fields."""
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
        mock_super_representation.return_value = self._make_quote_super_return(
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
        mock_super_representation.return_value = self._make_quote_super_return(
            citation_internal_link={"full_url": "/about/"},
        )
        block = QuoteBlock()

        representation = block.get_api_representation({})

        self.assertEqual(representation["citation_url"], "/about/")

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_returns_none_citation_url_when_no_links(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = self._make_quote_super_return(
            citation=None,
        )
        block = QuoteBlock()

        representation = block.get_api_representation({})

        self.assertIsNone(representation["citation_url"])


class ReviewBlockTests(SimpleTestCase):
    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_casts_stars_to_int(self, mock_super_representation):
        mock_super_representation.return_value = {
            "quote": "Loved it",
            "attribution": "Reviewer",
            "stars": "5",
        }
        block = ReviewBlock()

        representation = block.get_api_representation({"stars": "5"})

        self.assertEqual(representation["stars"], 5)


class PeopleListingBlockTests(SimpleTestCase):
    def test_get_api_representation_returns_empty_without_role(self):
        block = PeopleListingBlock()

        representation = block.get_api_representation({"role": None})

        self.assertEqual(representation, {})

    def test_get_api_representation_returns_empty_when_role_has_no_people(self):
        person_roles = Mock()
        person_roles.all.return_value.order_by.return_value = []
        role = SimpleNamespace(name="Author", person_roles=person_roles)
        block = PeopleListingBlock()

        representation = block.get_api_representation({"role": role})

        self.assertEqual(representation, {})

    @patch.object(DefaultPageSerializer, "to_representation")
    def test_get_api_representation_serializes_people_for_role(
        self, mock_to_representation
    ):
        person_page = object()
        mock_to_representation.return_value = {"id": 12, "title": "Ada Lovelace"}
        ordered_people = [
            SimpleNamespace(person=person_page),
            SimpleNamespace(person=None),
        ]
        person_roles = Mock()
        person_roles.all.return_value.order_by.return_value = ordered_people
        role = SimpleNamespace(name="Author", person_roles=person_roles)
        block = PeopleListingBlock()

        representation = block.get_api_representation({"role": role})

        self.assertEqual(representation["role"], "Author")
        self.assertEqual(
            representation["people"],
            [{"id": 12, "title": "Ada Lovelace"}, None],
        )
        mock_to_representation.assert_called_once_with(person_page)


class ShopCollectionBlockTests(SimpleTestCase):
    @patch("app.core.blocks.shop.ImageSerializer")
    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_adds_small_background_image(
        self, mock_super_representation, mock_serializer_class
    ):
        mock_super_representation.return_value = {"title": "Shop"}
        image = object()
        serializer = mock_serializer_class.return_value
        serializer.to_representation.return_value = {"jpeg": {"url": "/small.jpg"}}
        block = ShopCollectionBlock()

        representation = block.get_api_representation({"background_image": image})

        self.assertEqual(
            representation["background_image_small"],
            {"jpeg": {"url": "/small.jpg"}},
        )
        mock_serializer_class.assert_called_once_with(rendition_size="fill-600x400")
        serializer.to_representation.assert_called_once_with(image)

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_without_background_image_omits_small_rendition(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = {"title": "Shop"}
        block = ShopCollectionBlock()

        representation = block.get_api_representation({"background_image": None})

        self.assertNotIn("background_image_small", representation)


class DocumentBlockTests(SimpleTestCase):
    @staticmethod
    def _make_document(**overrides):
        """Build a document SimpleNamespace with sensible defaults; override per-test."""
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


class FeaturedPageBlockTests(SimpleTestCase):
    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_overrides_page_teaser_text(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = {
            "page": {"title": "Feature", "teaser_text": "Original teaser"},
            "teaser_text": "Override teaser",
        }
        block = FeaturedPageBlock()

        representation = block.get_api_representation(
            {"page": object(), "teaser_text": "Override teaser"}
        )

        self.assertEqual(representation["page"]["teaser_text"], "Override teaser")
        self.assertNotIn("teaser_text", representation)

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_without_teaser_override_keeps_original(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = {
            "page": {"title": "Feature", "teaser_text": "Original teaser"},
            "teaser_text": "",
        }
        block = FeaturedPageBlock()

        representation = block.get_api_representation(
            {"page": object(), "teaser_text": ""}
        )

        self.assertEqual(representation["page"]["teaser_text"], "Original teaser")
        self.assertNotIn("teaser_text", representation)
