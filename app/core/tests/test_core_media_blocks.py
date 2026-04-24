"""Testing style:
- Prefer real block values for smoke paths.
- Patch serializer/network boundaries only.
- Use superclass patching sparingly for nested block internals.
"""

from unittest.mock import patch

from app.core.blocks.image import (
    APIImageChooserBlock,
    ImageGalleryBlock,
    PartnerLogoChooserBlock,
)
from app.core.blocks.shop import ShopCollectionBlock
from django.test import SimpleTestCase


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
        mock_super_representation.return_value = {"title": "Gallery", "images": []}
        block = ImageGalleryBlock()
        value = {"images": [object(), object(), object()]}

        representation = block.get_api_representation(value)

        self.assertEqual(representation["count"], 3)
        self.assertEqual(representation["title"], "Gallery")

    @patch("wagtail.blocks.StructBlock.get_api_representation")
    def test_get_api_representation_uses_value_images_for_count(
        self, mock_super_representation
    ):
        mock_super_representation.return_value = {
            "title": "Gallery",
            "images": ["serialized-image"],
        }
        block = ImageGalleryBlock()
        value = {"images": [object(), object(), object()]}

        representation = block.get_api_representation(value)

        self.assertEqual(representation["count"], 3)
        self.assertEqual(representation["images"], ["serialized-image"])

    def test_get_api_representation_smoke_with_real_value(self):
        block = ImageGalleryBlock()
        value = block.to_python(
            {
                "title": "Gallery",
                "description": "",
                "images": [],
            }
        )

        representation = block.get_api_representation(value)

        self.assertEqual(representation["count"], 0)
        self.assertEqual(representation["images"], [])


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


class ShopCollectionBlockTests(SimpleTestCase):
    @staticmethod
    def _make_value(**overrides):
        value = {
            "title": "Shop",
            "description": "Description",
            "cta_text": "Shop now",
            "url": "https://example.com/shop",
            "background_image": object(),
        }
        value.update(overrides)
        return value

    @patch("app.core.blocks.shop.ImageSerializer")
    @patch("app.core.blocks.image.DetailedImageSerializer")
    def test_get_api_representation_adds_small_background_image(
        self,
        mock_detailed_serializer_class,
        mock_serializer_class,
    ):
        image = object()
        detailed_serializer = mock_detailed_serializer_class.return_value
        detailed_serializer.to_representation.return_value = {"id": 99}
        serializer = mock_serializer_class.return_value
        serializer.to_representation.return_value = {"jpeg": {"url": "/small.jpg"}}
        block = ShopCollectionBlock()

        representation = block.get_api_representation(
            self._make_value(background_image=image)
        )

        self.assertEqual(representation["background_image"], {"id": 99})
        self.assertEqual(
            representation["background_image_small"],
            {"jpeg": {"url": "/small.jpg"}},
        )
        mock_detailed_serializer_class.assert_called_once_with(
            rendition_size="fill-1800x720",
            jpeg_quality=60,
            webp_quality=70,
            background_colour="fff",
        )
        detailed_serializer.to_representation.assert_called_once_with(image)
        mock_serializer_class.assert_called_once_with(rendition_size="fill-600x400")
        serializer.to_representation.assert_called_once_with(image)

    @patch("app.core.blocks.image.DetailedImageSerializer")
    def test_get_api_representation_without_background_image_omits_small_rendition(
        self, mock_detailed_serializer_class
    ):
        detailed_serializer = mock_detailed_serializer_class.return_value
        detailed_serializer.to_representation.return_value = None
        block = ShopCollectionBlock()

        representation = block.get_api_representation(
            self._make_value(background_image=None)
        )

        self.assertIsNone(representation["background_image"])
        self.assertNotIn("background_image_small", representation)
