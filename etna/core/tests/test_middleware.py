from unittest.mock import patch
from urllib.parse import quote

from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.test import SimpleTestCase, TestCase, override_settings

from etna.core.middleware import InterpretCookiesMiddleware
from etna.core.test_utils import prevent_request_warnings


@override_settings(MAINTENANCE_MODE=True)
class TestMaintenanceMode(TestCase):
    @prevent_request_warnings
    def test_without_maintenance_mode_ends(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 503)
        self.assertNotIn("Retry-After", response.headers)

    @prevent_request_warnings
    @override_settings(MAINTENENCE_MODE_ENDS="2011-11-04T00:05:23+04:00")
    def test_maintenance_mode_ends_with_timezone_info(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 503)
        self.assertEquals(
            response.headers["Retry-After"], "Thu, 03 Nov 2011 20:05:23 GMT"
        )

    @prevent_request_warnings
    @override_settings(MAINTENENCE_MODE_ENDS="2011-11-04T00:05:23")
    def test_maintenance_mode_ends_without_timezone_info(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 503)
        self.assertEquals(
            response.headers["Retry-After"], "Fri, 04 Nov 2011 00:05:23 GMT"
        )

    @override_settings(MAINTENENCE_MODE_ALLOW_IPS=["123.4.5.6"])
    @patch("etna.core.middleware.get_client_ip", return_value="123.4.5.6")
    def test_maintenance_mode_bypassed_when_ip_in_allow_list(self, *args):
        response = self.client.get("/")

        self.assertEquals(response.status_code, 200)

    @prevent_request_warnings
    @override_settings(MAINTENENCE_MODE_ALLOW_IPS=["123.4.5.6"])
    @patch("etna.core.middleware.get_client_ip", return_value="789.0.1.2")
    def test_maintenance_mode_enforced_when_ip_not_in_allowed_list(
        self, mock_get_client_ip
    ):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 503)


class TestInterpretCookiesMiddleware(SimpleTestCase):
    usage_true = quote('{"usage":true,"settings":false,"essential":true}')
    usage_false = quote('{"usage":false,"settings":false,"essential":true}')
    empty = ""
    invalid = "NOT_JSON"
    unexpected_structure = '["item_one", "item_two"]'
    non_bool_usage = quote('{"usage":123,"settings":false,"essential":true}')

    def setUp(self):
        self.request = HttpRequest()
        self.request.path = "/"
        self.response = TemplateResponse(
            self.request, "home/home_page.html", context={}, status=200
        )

    def _apply_middleware(self):
        obj = InterpretCookiesMiddleware(None)
        obj.process_template_response(self.request, self.response)

    def test_default(self):
        self._apply_middleware()
        context_data = self.response.context_data
        self.assertIs(context_data["cookies_permitted"], False)
        self.assertIs(context_data["show_cookie_notice"], True)
        self.assertIs(context_data["show_beta_banner"], True)

    def test_cookies_permitted_value_when_preferences_cookie_set(self):
        for attribute_name, expected_cookies_permitted_value in (
            ("usage_true", True),
            ("usage_false", False),
            ("empty", False),
            ("invalid", False),
            ("unexpected_structure", False),
            ("non_bool_usage", False),
        ):
            with self.subTest(attribute_name):
                # set cookie value for request
                self.request.COOKIES["cookies_policy"] = getattr(self, attribute_name)
                # apply middelware to self.response
                self._apply_middleware()
                # check context_data
                self.assertIs(
                    self.response.context_data["cookies_permitted"],
                    expected_cookies_permitted_value,
                )

    @override_settings(FEATURE_COOKIE_BANNER_ENABLED=False)
    def test_show_cookie_notice_is_false_when_feature_disabled(self):
        self._apply_middleware()
        self.assertIs(self.response.context_data["show_cookie_notice"], False)

    def test_show_cookie_notice_is_false_when_hide_cookie_set(self):
        # set the 'hide cookie' value before applying
        self.request.COOKIES["dontShowCookieNotice"] = "true"
        self._apply_middleware()
        # check context_data
        self.assertIs(self.response.context_data["show_cookie_notice"], False)

    @override_settings(FEATURE_BETA_BANNER_ENABLED=False)
    def test_show_beta_banner_is_false_when_feature_disabled(self):
        self._apply_middleware()
        self.assertIs(self.response.context_data["show_beta_banner"], False)

    def test_show_beta_banner_is_false_when_hide_cookie_set(self):
        # set the 'hide cookie' value before applying
        self.request.COOKIES["beta_banner_dismissed"] = "true"
        self._apply_middleware()
        # check context_data
        self.assertIs(self.response.context_data["show_beta_banner"], False)
