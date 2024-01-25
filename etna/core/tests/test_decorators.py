from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse_lazy

from wagtail.test.utils import WagtailTestUtils

import responses

from ...ciim.tests.factories import (
    create_record,
    create_response,
    create_search_response,
)

CONDITIONALLY_PROTECTED_URLS = (
    reverse_lazy("search-catalogue"),
    reverse_lazy("details-page-machine-readable", kwargs={"id": "C140"}),
)


@override_settings(
    CLIENT_BASE_URL=f"{settings.CLIENT_BASE_URL}",
)
class SettingControlledLoginRequiredTest(WagtailTestUtils, TestCase):
    def setUp(self):
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/search",
            json=create_search_response(
                records=[
                    create_record(group="community", ciim_id="swop-49209"),
                    create_record(group="community", ciim_id="wmk-16758"),
                ]
            ),
        )
        responses.add(
            responses.GET,
            f"{settings.CLIENT_BASE_URL}/get",
            json=create_response(),
        )

    @override_settings(
        SEARCH_VIEWS_REQUIRE_LOGIN=True,
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
        RECORD_DETAIL_REQUIRE_LOGIN=True,
    )
    def test_allows_request_when_setting_value_is_true_and_authenticated(self):
        self.login()
        for url in CONDITIONALLY_PROTECTED_URLS:
            with self.subTest(f"URL: {url}"):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    @responses.activate
    @override_settings(
        SEARCH_VIEWS_REQUIRE_LOGIN=False,
        RECORD_DETAIL_REQUIRE_LOGIN=False,
    )
    def test_allows_unauthenticated_access_when_setting_value_is_false(self):
        for url in CONDITIONALLY_PROTECTED_URLS:
            with self.subTest(f"URL: {url}"):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
