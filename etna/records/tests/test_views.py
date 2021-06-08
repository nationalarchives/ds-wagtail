from django.test import TestCase, override_settings, RequestFactory

import responses

from .. import views


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    KONG_CLIENT_BASE_URL="https://kong.test",
    KONG_CLIENT_TEST_MODE=False,
)
class TestRecordPageDisambiguationView(TestCase):
    @responses.activate
    def test_no_matches_respond_with_404(self):
        responses.add(
            responses.GET,
            "https://kong.test/search",
            json={"hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}},
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
            json={
                "hits": {
                    "total": {"value": 2, "relation": "eq"},
                    "hits": [
                        {
                            "_source": {
                                "@admin": {
                                    "id": "C4122893",
                                },
                                "identifier": [
                                    {"reference_number": "ADM 223/3"},
                                ],
                            }
                        },
                        {
                            "_source": {
                                "@admin": {
                                    "id": "C4122893",
                                },
                                "identifier": [
                                    {"reference_number": "ADM 223/3"},
                                ],
                            }
                        },
                    ],
                }
            },
        )

        response = self.client.get("/catalogue/AD/2/2/")

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
            json={
                "hits": {
                    "total": {"value": 1, "relation": "eq"},
                    "hits": [
                        {
                            "_source": {
                                "@admin": {"id": "C4122893"},
                                "identifier": [
                                    {"reference_number": "ADM 223/3"},
                                ],
                            }
                        },
                    ],
                }
            },
        )

        response = self.client.get("/catalogue/AD/2/2/")

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
            responses.GET,
            "https://kong.test/fetch",
            json={"hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}},
        )

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.resolver_match.func, views.record_page_view)

    @responses.activate
    def test_record_page_rendered_for_single_result(self):
        responses.add(
            responses.GET,
            "https://kong.test/fetch",
            json={
                "hits": {
                    "total": {"value": 1, "relation": "eq"},
                    "hits": [
                        {
                            "_source": {
                                "@admin": {"id": "C4122893"},
                                "identifier": [
                                    {"reference_number": "ADM 223/3"},
                                ],
                            }
                        },
                    ],
                }
            },
        )

        response = self.client.get("/catalogue/C123456/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.func, views.record_page_view)
        self.assertTemplateUsed(response, "records/record_page.html")
