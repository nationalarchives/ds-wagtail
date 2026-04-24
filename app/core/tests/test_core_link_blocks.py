from types import SimpleNamespace

from app.core.blocks.cta import ButtonBlock
from app.core.blocks.links import (
    InternalLinkBlock,
    LinkBlock,
    LinkColumnWithHeaderBlock,
)
from app.generic_pages.factories import GeneralPageFactory
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.models import Site


class _LinkValue:
    def __init__(self, url, text, is_page, page_id=None, domain=""):
        self._url = url
        self._text = text
        self._is_page = is_page
        self._page_id = page_id
        self._domain = domain

    def url(self):
        return self._url

    def text(self):
        return self._text

    def is_page(self):
        return self._is_page

    def page_id(self):
        return self._page_id

    def external_domain(self):
        return self._domain


def _make_button_value(**overrides):
    value = {
        "label": "Visit",
        "link": SimpleNamespace(full_url="https://example.com/internal"),
        "external_link": "",
        "accented": False,
    }
    value.update(overrides)
    return value


class PageValidationTestMixin:
    @classmethod
    def setUpTestData(cls):
        root = Site.objects.get(is_default_site=True).root_page
        cls.linked_page = GeneralPageFactory(parent=root, title="Linked page")


class ButtonBlockTests(PageValidationTestMixin, TestCase):
    def test_clean_rejects_both_page_and_external_link(self):
        value = {
            "label": "Read more",
            "link": self.linked_page,
            "external_link": "https://example.com",
            "accented": False,
        }
        block = ButtonBlock()

        with self.assertRaises(ValidationError) as context:
            block.clean(value)

        self.assertIn(
            "either a page link or an external link, not both", str(context.exception)
        )

    def test_clean_requires_a_link(self):
        value = {
            "label": "Read more",
            "link": None,
            "external_link": "",
            "accented": False,
        }
        block = ButtonBlock()

        with self.assertRaises(ValidationError) as context:
            block.clean(value)

        self.assertIn(
            "You must provide either a page link or an external link",
            str(context.exception),
        )

    def test_get_api_representation_prefers_external_link_and_defaults_accent(self):
        block = ButtonBlock()
        value = _make_button_value(
            external_link="https://example.com/external", accented=None
        )

        representation = block.get_api_representation(value)

        self.assertEqual(
            representation,
            {
                "label": "Visit",
                "href": "https://example.com/external",
                "accent": False,
            },
        )

    def test_get_api_representation_uses_internal_link_when_no_external_link(self):
        block = ButtonBlock()
        value = _make_button_value(label="Visit us", accented=True)

        representation = block.get_api_representation(value)

        self.assertEqual(
            representation,
            {
                "label": "Visit us",
                "href": "https://example.com/internal",
                "accent": True,
            },
        )


class LinkBlockTests(PageValidationTestMixin, TestCase):
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

    def test_link_block_clean_rejects_both_page_and_external_link(self):
        value = {
            "page": self.linked_page,
            "title": "Both set",
            "external_link": "https://example.com",
        }
        block = LinkBlock()

        with self.assertRaises(StructBlockValidationError) as context:
            block.clean(value)

        self.assertIn("page", context.exception.block_errors)
        self.assertIn("external_link", context.exception.block_errors)

    def test_internal_link_get_api_representation_uses_struct_value_helpers(self):
        block = InternalLinkBlock()
        value = _LinkValue(url="/visit-us", text="Visit us", is_page=True, page_id=42)

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
        first_link = _LinkValue(url="/one", text="One", is_page=True)
        second_link = _LinkValue(
            url="https://example.com/two", text="Two", is_page=False
        )

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
