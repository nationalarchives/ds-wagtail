import io
import re

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from wagtail.core.models import Group

import responses

from ...ciim.tests.factories import create_media, create_record, create_response

User = get_user_model()


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
)
class TestRecordDisambiguationView(TestCase):
    def setUp(self):
        private_beta_user = User(
            username="private-beta@email.com", email="private-beta@email.com"
        )
        private_beta_user.set_password("password")
        private_beta_user.save()
        private_beta_user.groups.add(Group.objects.get(name="Beta Testers"))

        self.client.login(email="private-beta@email.com", password="password")

    @responses.activate
    def test_no_matches_respond_with_404(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(records=[]),
        )

        response = self.client.get("/catalogue/AD/2/2/")

        self.assertEquals(
            response.resolver_match.view_name, "details-page-human-readable"
        )
        self.assertEquals(response.status_code, 404)

    @responses.activate
    def test_disambiguation_page_rendered_for_multiple_results(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[
                    create_record(reference_number="ADM 223/3"),
                    create_record(reference_number="ADM 223/3"),
                ]
            ),
        )

        response = self.client.get("/catalogue/ADM/223/3/")

        self.assertEquals(
            response.resolver_match.view_name, "details-page-human-readable"
        )
        self.assertTemplateUsed(response, "records/record_disambiguation_page.html")

    @responses.activate
    def test_rendering_deferred_to_details_page_view(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[
                    create_record(iaid="C123456", reference_number="ADM 223/3"),
                ]
            ),
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", reference_number="ADM 223/3"),
                ]
            ),
        )

        response = self.client.get("/catalogue/ADM/223/3/", follow=False)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.resolver_match.view_name, "details-page-human-readable"
        )
        self.assertTemplateUsed(response, "records/record_page.html")


@override_settings(
    KONG_CLIENT_BASE_URL="https://kong.test",
)
class TestRecordView(TestCase):
    def setUp(self):
        private_beta_user = User(
            username="private-beta@email.com", email="private-beta@email.com"
        )
        private_beta_user.set_password("password")
        private_beta_user.save()
        private_beta_user.groups.add(Group.objects.get(name="Beta Testers"))

        self.client.login(email="private-beta@email.com", password="password")

    @responses.activate
    def test_no_matches_respond_with_404(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(records=[]),
        )

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 404)
        self.assertEquals(
            response.resolver_match.view_name, "details-page-machine-readable"
        )

    @responses.activate
    def test_record_rendered_for_single_result(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456"),
                ]
            ),
        )

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.resolver_match.view_name, "details-page-machine-readable"
        )
        self.assertTemplateUsed(response, "records/record_page.html")

    @responses.activate
    def test_record_renders_for_record_with_no_image(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(records=[]),
        )

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.resolver_match.view_name, "details-page-machine-readable"
        )
        self.assertTemplateUsed(response, "records/record_page.html")
        self.assertTemplateNotUsed(response, "records/image-viewer-panel.html")

    @responses.activate
    def test_record_renders_for_record_with_image(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )

        responses.add(
            responses.GET,
            "https://kong.test/data/search",
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
)
class TestImageBrowseView(TestCase):
    def setUp(self):
        private_beta_user = User(
            username="private-beta@email.com", email="private-beta@email.com"
        )
        private_beta_user.set_password("password")
        private_beta_user.save()
        private_beta_user.groups.add(Group.objects.get(name="Beta Testers"))

        self.client.login(email="private-beta@email.com", password="password")

    @responses.activate
    def test_image_browse_non_digitised_record(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
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
            "https://kong.test/data/fetch",
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
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
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
)
class TestImageViewerView(TestCase):
    def setUp(self):
        private_beta_user = User(
            username="private-beta@email.com", email="private-beta@email.com"
        )
        private_beta_user.set_password("password")
        private_beta_user.save()
        private_beta_user.groups.add(Group.objects.get(name="Beta Testers"))

        self.client.login(email="private-beta@email.com", password="password")

    @responses.activate
    def test_image_browse_non_digitised_record(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
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
            "https://kong.test/data/fetch",
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
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[
                    create_media(location="path/to/previous-image.jpeg", sort="01"),
                    create_media(location="path/to/image.jpeg", sort="02"),
                    create_media(location="path/to/next-image.jpeg", sort="03"),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/media",
            body="",
            stream=True,
        )

        response = self.client.get("/records/images/C123456/02/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.url_name, "image-viewer")
        self.assertEquals(
            response.context["previous_image"].location, "path/to/previous-image.jpeg"
        )
        self.assertEquals(response.context["image"].location, "path/to/image.jpeg")
        self.assertEquals(
            response.context["next_image"].location, "path/to/next-image.jpeg"
        )

    @responses.activate
    def test_no_next_image(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[
                    create_media(location="path/to/previous-image.jpeg", sort="01"),
                    create_media(location="path/to/image.jpeg", sort="02"),
                ]
            ),
        )

        response = self.client.get("/records/images/C123456/02/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.url_name, "image-viewer")
        self.assertEquals(
            response.context["previous_image"].location, "path/to/previous-image.jpeg"
        )
        self.assertEquals(response.context["image"].location, "path/to/image.jpeg")
        self.assertEquals(response.context["next_image"], None)

    @responses.activate
    def test_no_previous_image(self):
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[
                    create_media(location="path/to/image.jpeg", sort="01"),
                    create_media(location="path/to/next-image.jpeg", sort="02"),
                ]
            ),
        )

        response = self.client.get("/records/images/C123456/01/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.url_name, "image-viewer")
        self.assertEquals(response.context["previous_image"], None)
        self.assertEquals(response.context["image"].location, "path/to/image.jpeg")
        self.assertEquals(
            response.context["next_image"].location, "path/to/next-image.jpeg"
        )

    @responses.activate
    def test_previous_image_but_no_selected_image(self):
        """Modifying the URL to attempt to display image_count + 1 image should 404."""

        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json=create_response(
                records=[
                    create_media(location="path/to/previous-image.jpeg", sort="01"),
                ]
            ),
        )

        response = self.client.get("/records/images/C123456/02/")

        self.assertEquals(response.status_code, 404)

    @responses.activate
    def test_invalid_response_from_kong_raises_404(self):
        """It's possible for us to pass a very long offset to Kong that returns a 400.

        In such an event, ensure that we gracefully handle the error."""
        responses.add(
            responses.GET,
            "https://kong.test/data/fetch",
            json=create_response(
                records=[
                    create_record(iaid="C123456", is_digitised=True),
                ]
            ),
        )
        responses.add(
            responses.GET,
            "https://kong.test/data/search",
            json={
                "timestamp": "2021-08-26T09:07:31.688+00:00",
                "status": 400,
                "error": "Bad Request",
                "message": """
                  Failed to convert value of type 'java.lang.String' to required type 'java.lang.Integer';
                  nested exception is java.lang.NumberFormatException: For input string: \"999999999999999999\"
                  """,
                "path": "/search",
            },
            status=400,
        )

        response = self.client.get("/records/images/C123456/11000000000000000000/")

        self.assertEquals(response.status_code, 404)
