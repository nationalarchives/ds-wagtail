import io
import re

from django.test import TestCase, override_settings
from django.urls import reverse

import responses

from .. import views
from ...ciim.tests.factories import create_record, create_media, create_response


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_CLIENT_TEST_MODE=False,
)
class TestRecordPageDisambiguationView(TestCase):
    @responses.activate
    def test_no_matches_respond_with_404(self):
        responses.add(
            responses.GET, "https://kong.test/search", json=create_response(records=[])
        )

        response = self.client.get("/catalogue/AD/2/2/")

        self.assertEquals(response.resolver_match.view_name, 'details-page-human-readable')
        self.assertEquals(response.status_code, 404)

    @responses.activate
    def test_disambiguation_page_rendered_for_multiple_results(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(
                records=[
                    create_record(reference_number="ADM 223/3"),
                    create_record(reference_number="ADM 223/3"),
                ]
            ),
        )

        response = self.client.get("/catalogue/ADM/223/3/")

        self.assertEquals(response.resolver_match.view_name, 'details-page-human-readable')
        self.assertTemplateUsed(response, "records/record_disambiguation_page.html")

    @responses.activate
    def test_rendering_deferred_to_details_page_view(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(
                records=[
                    create_record(iaid="C123456", reference_number="ADM 223/3"),
                ]
            ),
        )

        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", reference_number="ADM 223/3"),
                ]
            ),
        )

        response = self.client.get("/catalogue/ADM/223/3/", follow=False)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.view_name, 'details-page-human-readable')
        self.assertTemplateUsed(response, "records/record_page.html")


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_CLIENT_TEST_MODE=False,
)
class TestRecordPageView(TestCase):
    @responses.activate
    def test_no_matches_respond_with_404(self):
        responses.add(
            responses.GET, "https://kong.test/fetch", json=create_response(records=[])
        )

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.resolver_match.view_name, 'details-page-machine-readable')

    @responses.activate
    def test_record_page_rendered_for_single_result(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456"),
                ]
            ),
        )

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.view_name, 'details-page-machine-readable')
        self.assertTemplateUsed(response, "records/record_page.html")

    @responses.activate
    def test_record_page_renders_for_record_with_no_image(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )

        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(records=[]),
        )

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.view_name, 'details-page-machine-readable')
        self.assertTemplateUsed(response, "records/record_page.html")
        self.assertTemplateNotUsed(response, "records/image-viewer-panel.html")

    @responses.activate
    def test_record_page_renders_for_record_with_image(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )

        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(
                records=[
                    create_media(),
                ]
            ),
        )

        responses.add(
            responses.GET,
            "https://kong.test/media",
            body="",
            stream=True,
        )

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "records/record_page.html")
        self.assertTemplateUsed(response, "includes/records/image-viewer-panel.html")


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_CLIENT_TEST_MODE=False,
)
class TestImageServeView(TestCase):
    def test_no_location_404s(self):
        response = self.client.get("/records/media/")

        self.assertEquals(response.status_code, 404)

    @responses.activate
    def test_404_response_from_kong_is_forwarded(self):
        responses.add(
            responses.GET,
            re.compile("^https://kong.test/media"),
            status=404,
        )

        response = self.client.get("/records/image/missing/image.jpeg")

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.resolver_match.url_name, "image-serve")

    @responses.activate
    def test_success(self):
        responses.add(
            responses.GET,
            re.compile("^https://kong.test/media"),
            body=io.BufferedReader(io.BytesIO(b"test byte stream")),
            content_type="application/octet-stream",
            stream=True,
        )

        response = self.client.get("/records/image/valid/path.jpg")

        self.assertEquals(response["content-type"], "image/jpeg")
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.streaming)


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_CLIENT_TEST_MODE=False,
)
class TestImageBrowseView(TestCase):
    @responses.activate
    def test_image_browse_non_digitised_record(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=False),
                ]
            ),
        )
        response = self.client.get("/records/images/C123456/")

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.resolver_match.url_name, "image-browse")

    @responses.activate
    def test_image_browse_record_with_no_media(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="C123456", is_digitised=True, media_reference_id=None
                    ),
                ]
            ),
        )
        response = self.client.get("/records/images/C123456/")

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.resolver_match.url_name, "image-browse")

    @responses.activate
    def test_success(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(
                records=[
                    create_media(),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/media",
            body="",
            stream=True,
        )

        response = self.client.get("/records/images/C123456/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.url_name, "image-browse")


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_CLIENT_TEST_MODE=False,
)
class TestImageViewerView(TestCase):
    @responses.activate
    def test_image_browse_non_digitised_record(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=False),
                ]
            ),
        )
        response = self.client.get("/records/images/C123456/01/")

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.resolver_match.url_name, "image-viewer")

    @responses.activate
    def test_image_browse_record_with_no_media(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="C123456", is_digitised=True, media_reference_id=None
                    ),
                ]
            ),
        )
        response = self.client.get("/records/images/C123456/01/")

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.resolver_match.url_name, "image-viewer")

    @responses.activate
    def test_success(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(
                records=[
                    create_media(location="path/to/previous-image.jpeg"),
                    create_media(location="path/to/image.jpeg"),
                    create_media(location="path/to/next-image.jpeg"),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/media",
            body="",
            stream=True,
        )

        response = self.client.get("/records/images/C123456/01/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.url_name, "image-viewer")
