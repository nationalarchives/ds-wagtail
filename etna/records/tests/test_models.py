import unittest

from django.test import TestCase, override_settings

import responses

from ...ciim.tests.factories import create_media, create_response
from ..models import Image


@unittest.skip(
    "Kong open beta API does not support media. Re-enable/update once media is available."
)
@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class ImageTestCase(TestCase):
    @responses.activate
    def test_thumbnail_url(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[
                    create_media(
                        thumbnail_location="path/to/thumbnail.jpeg",
                        location="path/to/image.jpeg",
                    ),
                ]
            ),
        )

        images = Image.search.filter(rid="")
        image = images[0]

        self.assertEquals(
            image.thumbnail_url, "https://media.preview/path/to/thumbnail.jpeg"
        )

    @responses.activate
    def test_thumbnail_url_fallback(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[
                    create_media(
                        thumbnail_location=None, location="path/to/image.jpeg"
                    ),
                ]
            ),
        )

        images = Image.search.filter(rid="")
        image = images[0]

        # Fallback serves image through Wagtail instead of from kong
        self.assertEquals(image.thumbnail_url, "/records/image/path/to/image.jpeg")
