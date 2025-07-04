from urllib.parse import quote

from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.test import SimpleTestCase, override_settings

from app.core.middleware import InterpretCookiesMiddleware


class TestInterpretCookiesMiddleware(SimpleTestCase):
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

    def test_behaviour_when_context_data_is_none(self):
        self.response.context_data = None
        self._apply_middleware()
        context_data = self.response.context_data
        self.assertIs(context_data["cookies_permitted"], False)
        self.assertIs(context_data["show_cookie_notice"], True)

    def test_context_not_modified_for_excluded_paths_and_subpaths(self):
        for test_path in (
            "/admin/",
            "/admin/pages/",
            "/django-admin/",
            "/django-admin/sites/",
            "/documents/1/some-example-filename.pdf",
        ):
            self.request.path = test_path
            self._apply_middleware()
            context_data = self.response.context_data
            self.assertNotIn("cookies_permitted", context_data)
            self.assertNotIn("show_cookie_notice", context_data)

    def test_cookies_permitted_is_true_when_usage_is_true(self):
        # set cookie value for request
        self.request.COOKIES["cookies_policy"] = quote(
            '{"usage":true,"settings":false,"essential":true}'
        )
        # apply middelware to self.response
        self._apply_middleware()
        # check context data value
        self.assertIs(self.response.context_data["cookies_permitted"], True)

    def test_cookies_permitted_is_false_when_usage_is_false(self):
        # set cookie value for request
        self.request.COOKIES["cookies_policy"] = quote(
            '{"usage":false,"settings":false,"essential":true}'
        )
        # apply middelware to self.response
        self._apply_middleware()
        # check context data value
        self.assertIs(self.response.context_data["cookies_permitted"], False)

    def test_cookies_permitted_is_false_when_value_is_unexpected(self):
        for subtest_name, cookie_value in (
            ("empty string", ""),
            ("invalid", "NOT_JSON"),
            ("unexpected json structure", '["item_one", "item_two"]'),
            (
                "usage is not a bool",
                quote('{"usage":123,"settings":false,"essential":true}'),
            ),
        ):
            with self.subTest(subtest_name):
                # set cookie value for request
                self.request.COOKIES["cookies_policy"] = cookie_value
                # apply middelware to self.response
                self._apply_middleware()
                # check context_data
                self.assertIs(
                    self.response.context_data["cookies_permitted"],
                    False,
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
