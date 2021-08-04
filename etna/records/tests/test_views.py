from django.test import TestCase, override_settings, RequestFactory

import responses

from .. import views
from ...ciim.tests.factories import create_record, create_media, create_response


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
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

        self.assertEquals(response.status_code, 404)
        self.assertEquals(
            response.resolver_match.func, views.record_page_disambiguation_view
        )

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

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.resolver_match.func, views.record_page_disambiguation_view
        )
        self.assertTemplateUsed(response, "records/record_disambiguation_page.html")

    @responses.activate
    def test_record_page_rendered_for_single_result(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json=create_response(
                records=[
                    create_record(reference_number="ADM 223/3"),
                ]
            ),
        )

        response = self.client.get("/catalogue/ADM/223/3/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.resolver_match.func, views.record_page_disambiguation_view
        )
        self.assertTemplateUsed(response, "records/record_page.html")


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
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
        self.assertEquals(response.resolver_match.func, views.record_page_view)

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
        self.assertEquals(response.resolver_match.func, views.record_page_view)
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

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.func, views.record_page_view)
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
        self.assertEquals(response.resolver_match.func, views.record_page_view)
        self.assertTemplateUsed(response, "records/record_page.html")
        self.assertTemplateUsed(response, "includes/records/image-viewer-panel.html")
