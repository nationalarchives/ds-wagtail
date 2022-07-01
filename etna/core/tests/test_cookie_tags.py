from django.test import SimpleTestCase

from etna.core.templatetags.cookie_tags import cookie_use_permitted


class TestCookieUsePermittedTag(SimpleTestCase):

    empty_cookie = ""
    none_cookie = None
    json_usage_true_cookie = '{"usage":true,"settings":false,"essential":true}'
    json_unicoded_usage_true_cookie = (
        "%7b%22usage%22%3atrue%2c%22settings%22%3afalse%2c%22essential%22%3atrue%7d"
    )
    json_usage_false_cookie = '{"usage":false,"settings":false,"essential":true}'

    def test_default(self):
        for attribute_name, expected_result in (
            ("empty_cookie", False),
            ("none_cookie", False),
            ("json_usage_true_cookie", True),
            ("json_unicoded_usage_true_cookie", True),
            ("json_usage_false_cookie", False),
        ):
            with self.subTest(attribute_name):
                source = getattr(self, attribute_name)

                self.assertEqual(cookie_use_permitted(source), expected_result)
