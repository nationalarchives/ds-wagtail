from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse_lazy

from wagtail.test.utils import WagtailTestUtils

import responses

from ...ciim.tests.factories import create_record, create_response

CONDITIONALLY_PROTECTED_URLS = (
    reverse_lazy("search-catalogue"),
    reverse_lazy("details-page-machine-readable", kwargs={"iaid": "C140"}),
)


@override_settings(
    KONG_CLIENT_BASE_URL=f"{settings.KONG_CLIENT_BASE_URL}",
    KONG_IMAGE_PREVIEW_BASE_URL="https://media.preview/",
)
class SettingControlledLoginRequiredTest(WagtailTestUtils, TestCase):
    def setUp(self):
        responses.add(
            responses.GET,
            f"{settings.KONG_CLIENT_BASE_URL}/search",
            json={
                "responses": [
                    create_response(),
                    create_response(),
                ]
            },
        )
        responses.add(
            responses.GET,
            f"{settings.KONG_CLIENT_BASE_URL}/fetch",
            json=create_response(
                records=[
                    create_record(
                        iaid="C123456",
                        description=[{"value": "This is the description from Kong"}],
                    )
                ]
            ),
        )

    @override_settings(
        SEARCH_VIEWS_REQUIRE_LOGIN=True,
        IMAGE_VIEWER_REQUIRE_LOGIN=True,
        RECORD_DETAIL_REQUIRE_LOGIN=True,
    )
    def test_requires_login_when_setting_value_is_true(self):
        for url in CONDITIONALLY_PROTECTED_URLS:
            with self.subTest(f"URL: {url}"):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f"/accounts/login?next={url}",
                    fetch_redirect_response=False,
                )

    @responses.activate
    @override_settings(
        SEARCH_VIEWS_REQUIRE_LOGIN=True,
        IMAGE_VIEWER_REQUIRE_LOGIN=True,
        RECORD_DETAIL_REQUIRE_LOGIN=True,
    )
    def test_allows_request_when_setting_value_is_true_and_authenticated(self):
        self.login()
        for url in CONDITIONALLY_PROTECTED_URLS:
            with self.subTest(f"URL: {url}"):
                response = self.client.get(url)
                self.assertEquals(response.status_code, 200)

    @responses.activate
    @override_settings(
        SEARCH_VIEWS_REQUIRE_LOGIN=False,
        IMAGE_VIEWER_REQUIRE_LOGIN=False,
        RECORD_DETAIL_REQUIRE_LOGIN=False,
    )
    def test_allows_unauthenticated_access_when_setting_value_is_false(self):
        for url in CONDITIONALLY_PROTECTED_URLS:
            with self.subTest(f"URL: {url}"):
                response = self.client.get(url)
                self.assertEquals(response.status_code, 200)
